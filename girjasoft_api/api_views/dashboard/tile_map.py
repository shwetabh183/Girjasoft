"""Map legacy dashboard chart_id values to Next.js tile element ids."""

CHART_ID_TO_TILE: dict[str, str] = {
    "offline_employees": "notInYetId",
    "online_employees": "notoutYetId",
    "overall_leave_chart": "movable1",
    "hired_candidates": "movable2",
    "onboarding_candidates": "movable3",
    "recruitment_analytics": "movable8",
    "attendance_analytic": "movable4",
    "hours_chart": "pendingHours",
    "employees_chart": "movable5",
    "department_chart": "movable6",
    "gender_chart": "movable7",
    "objective_status": "movable9",
    "key_result_status": "movable10",
    "feedback_status": "movable11",
    "shift_request_approve": "shiftRequestApprove",
    "work_type_request_approve": "WorkTypeRequestApprove",
    "overtime_approve": "OTApprove",
    "attendance_validate": "AttendanceValidate",
    "leave_request_approve": "LeaveApprove",
    "leave_allocation_approve": "LeaveAllocationApprove",
    "feedback_answer": "feedbackAnswer",
    "asset_request_approve": "assetRequestApprove",
}

TILE_TO_CHART_ID: dict[str, str] = {tile: chart for chart, tile in CHART_ID_TO_TILE.items()}


def hidden_tile_ids(chart_ids: list[str] | None) -> list[str]:
    if not chart_ids:
        return []
    return [CHART_ID_TO_TILE[cid] for cid in chart_ids if cid in CHART_ID_TO_TILE]


def chart_id_for_tile(tile_id: str) -> str | None:
    return TILE_TO_CHART_ID.get(tile_id)
