import asyncio
import csv
import io
import json
import threading

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.config import DEEPSEEK_BASE_URL, DEFAULT_TEMPERATURE, REQUEST_TIMEOUT
from app.models.payload import TargetType
from app.models.scan import ScanRequest, ScanStatusResponse
from app.payloads.registry import get_by_ids, get_by_target_type
from app.rate_limit import limiter
from app.runner import run_scan, summarize_results
from app.scan_store import create_scan, get_scan
from app.targets.direct_chat import DirectChatTarget
from app.targets.rag_target import RAGTarget
from app.targets.tool_agent import ToolAgentTarget

router = APIRouter()

_TARGET_BUILDERS = {
    TargetType.DIRECT_CHAT: DirectChatTarget,
    TargetType.TOOL_AGENT: ToolAgentTarget,
    TargetType.RAG: RAGTarget,
}


def _build_llm(req: ScanRequest):
    if req.provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=req.model,
            temperature=DEFAULT_TEMPERATURE,
            google_api_key=req.api_key,
            timeout=REQUEST_TIMEOUT,
        )
    if req.provider == "deepseek":
        return ChatOpenAI(
            model=req.model,
            temperature=DEFAULT_TEMPERATURE,
            api_key=req.api_key,
            base_url=DEEPSEEK_BASE_URL,
            timeout=REQUEST_TIMEOUT,
        )
    raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")


def _build_target(req: ScanRequest):
    llm = _build_llm(req)
    builder = _TARGET_BUILDERS.get(req.target_type)
    if builder is None:
        raise HTTPException(status_code=400, detail=f"Unknown target type: {req.target_type}")
    return builder(llm, system_prompt=req.system_prompt), llm


def _run_in_background(scan_id: str, req: ScanRequest) -> None:
    state = get_scan(scan_id)
    assert state is not None
    state.status = "running"

    try:
        target, judge_llm = _build_target(req)
        payloads = (
            get_by_ids(req.selected_payload_ids)
            if req.selected_payload_ids
            else get_by_target_type(req.target_type)
        )

        for item in run_scan(
            target=target,
            payloads=payloads,
            goal=req.goal,
            system_prompt=req.system_prompt,
            eval_mode=req.eval_mode,
            judge_llm=judge_llm,
            should_cancel=state.cancel_event.is_set,
        ):
            state.append_result(item)

        state.summary = summarize_results(state.snapshot_results())
        state.status = "cancelled" if state.cancel_event.is_set() else "completed"

    except Exception as e:
        state.error = str(e)
        state.status = "error"


@router.post("/scans")
@limiter.limit("5/hour")
def start_scan(request: Request, req: ScanRequest):
    payloads = (
        get_by_ids(req.selected_payload_ids)
        if req.selected_payload_ids
        else get_by_target_type(req.target_type)
    )
    state = create_scan(req.target_type, total_payloads=len(payloads))

    thread = threading.Thread(target=_run_in_background, args=(state.id, req), daemon=True)
    thread.start()

    return {"scan_id": state.id}


def _status_response(state) -> ScanStatusResponse:
    return ScanStatusResponse(
        scan_id=state.id,
        status=state.status,
        target_type=state.target_type,
        progress={
            "completed": len(state.results),
            "total": state.total_payloads,
            "current_payload_name": state.current_payload_name,
        },
        results=state.snapshot_results(),
        summary=state.summary,
        error=state.error,
        created_at=state.created_at,
    )


@router.get("/scans/{scan_id}")
def get_scan_status(scan_id: str) -> ScanStatusResponse:
    state = get_scan(scan_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return _status_response(state)


@router.post("/scans/{scan_id}/cancel")
def cancel_scan(scan_id: str):
    state = get_scan(scan_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    state.cancel_event.set()
    return {"status": "cancelling"}


@router.get("/scans/{scan_id}/stream")
async def stream_scan(scan_id: str):
    state = get_scan(scan_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    async def event_generator():
        sent = 0
        while True:
            results = state.snapshot_results()
            while sent < len(results):
                yield f"event: result\ndata: {results[sent].model_dump_json()}\n\n"
                sent += 1

            if state.status in ("completed", "cancelled", "error"):
                payload = _status_response(state).model_dump_json()
                yield f"event: done\ndata: {payload}\n\n"
                return

            await asyncio.sleep(0.2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/scans/{scan_id}/export")
def export_scan(scan_id: str, format: str = "json"):
    state = get_scan(scan_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    results = state.snapshot_results()

    if format == "csv":
        buffer = io.StringIO()
        fieldnames = [
            "id", "category", "name", "kind", "is_control", "success",
            "confidence", "severity", "triggered_tools", "reason", "duration_ms", "error",
        ]
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row = r.model_dump()
            row["triggered_tools"] = ";".join(row["triggered_tools"])
            writer.writerow({k: row[k] for k in fieldnames})
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.csv"},
        )

    body = json.dumps(
        {
            "summary": state.summary.model_dump() if state.summary else None,
            "results": [r.model_dump() for r in results],
        },
        indent=2,
        default=str,
    )
    return StreamingResponse(
        iter([body]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.json"},
    )
