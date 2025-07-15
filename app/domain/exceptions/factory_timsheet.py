from app.domain.exceptions.base import DomainException


def user_timesheet_not_found(
    user_id: str, week_start: str = None
) -> DomainException:
    details = (
        f"User with id {user_id} does not have a timesheet submitted"
        f"for the week starting {week_start}"
        if week_start
        else f"User with id {user_id} does not have any timesheets submitted"
    )
    return DomainException(
        message="Timesheet not found", details=details, http_code=404
    )


def duplicate_timesheet(user_id: str, week_start: str) -> DomainException:
    return DomainException(
        message="Duplicate timesheet",
        details=f"User {user_id} has already submitted a timesheet for week "
        f"starting {week_start}",
        http_code=409,
    )


def timesheet_not_found(timesheet_id: str) -> DomainException:
    return DomainException(
        message="Timesheet not found",
        details=f"Timesheet with id {timesheet_id} was not found !",
        http_code=404,
    )


def timesheet_already_approved(timesheet_id: str) -> DomainException:
    return DomainException(
        message="Timesheet already approved",
        details=f"Timesheet with id {timesheet_id} was already approved!",
        http_code=409,
    )


def duplicate_time_entry(day: str) -> DomainException:
    return DomainException(
        message="Duplicate time entry",
        details=f"Multiple entries found for day {day}",
        http_code=400,
    )


def permission_denied(reason: str) -> DomainException:
    return DomainException(
        message="Permission denied", details=reason, http_code=403
    )
