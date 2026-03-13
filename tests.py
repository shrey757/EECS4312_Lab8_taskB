import pytest

from solution import EventRegistration, UserStatus, OperationResult


# Covers C1, C2, C5, C6 | AC1
def test_fifo_promotion_order():
    er = EventRegistration(capacity=2)

    assert er.register("u1") == OperationResult(UserStatus("registered"))
    assert er.register("u2") == OperationResult(UserStatus("registered"))
    assert er.register("u3") == OperationResult(UserStatus("waitlisted", 1))
    assert er.register("u4") == OperationResult(UserStatus("waitlisted", 2))

    result = er.cancel("u1")

    assert result == OperationResult(
        status=UserStatus("not_found"),
        explanation="registration cancelled: u3 was promoted from the waitlist due to the open slot"
    )
    assert er.snapshot()["registered"] == ["u2", "u3"]
    assert er.snapshot()["waitlist"] == ["u4"]


# Covers C2, C8 | AC2, AC9
def test_automatic_promotion_after_cancellation():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")

    result = er.cancel("u1")

    assert result.status == UserStatus("not_found")
    assert "u2 was promoted" in result.explanation
    assert er.status("u2") == UserStatus("registered")


# Covers C3 | AC3, AC16
def test_status_queries_return_registered_and_waitlist_position():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")

    assert er.status("u1") == UserStatus("registered")
    assert er.status("u2") == UserStatus("waitlisted", 1)


# Covers C4, C7 | AC4, AC10, AC11
def test_duplicate_registration_rejected_for_registered_user_and_state_unchanged():
    er = EventRegistration(capacity=1)
    er.register("u1")

    before = er.snapshot()
    result = er.register("u1")
    after = er.snapshot()

    assert result == OperationResult(
        status=UserStatus("registered"),
        explanation="duplicate registration rejected: user is already registered"
    )
    assert before == after


# Covers C4, C7 | AC10, AC11
def test_duplicate_registration_rejected_for_waitlisted_user_and_state_unchanged():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")

    before = er.snapshot()
    result = er.register("u2")
    after = er.snapshot()

    assert result == OperationResult(
        status=UserStatus("waitlisted", 1),
        explanation="duplicate registration rejected: user is already waitlisted"
    )
    assert before == after


# Covers C7 | AC14
def test_waitlist_cancellation_preserves_order():
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.register("u4")
    er.register("u5")

    result = er.cancel("u4")

    assert result == OperationResult(
        status=UserStatus("not_found"),
        explanation="waitlist entry cancelled"
    )
    assert er.snapshot()["waitlist"] == ["u3", "u5"]


# Covers C7 | AC6
def test_capacity_zero_puts_all_users_on_waitlist():
    er = EventRegistration(capacity=0)

    assert er.register("u1") == OperationResult(UserStatus("waitlisted", 1))
    assert er.register("u2") == OperationResult(UserStatus("waitlisted", 2))
    assert er.snapshot()["registered"] == []
    assert er.snapshot()["waitlist"] == ["u1", "u2"]


# Covers C7, C8 | AC7, AC11, AC17
def test_cancel_nonexistent_user_returns_not_found_and_preserves_state():
    er = EventRegistration(capacity=1)
    er.register("u1")

    before = er.snapshot()
    result = er.cancel("missing")
    after = er.snapshot()

    assert result == OperationResult(
        status=UserStatus("not_found"),
        explanation="cancellation rejected: user not found"
    )
    assert before == after


# Covers C3, C7 | AC12
def test_nonexistent_status_query_returns_not_found():
    er = EventRegistration(capacity=2)
    assert er.status("unknown") == UserStatus("not_found")


# Covers C5, C6 | AC5
def test_identical_sequences_produce_same_result():
    er1 = EventRegistration(capacity=2)
    er2 = EventRegistration(capacity=2)

    for system in (er1, er2):
        system.register("u1")
        system.register("u2")
        system.register("u3")
        system.cancel("u1")
        system.register("u4")

    assert er1.snapshot() == er2.snapshot()
    assert er1.status("u2") == er2.status("u2")
    assert er1.status("u3") == er2.status("u3")
    assert er1.status("u4") == er2.status("u4")


# Covers C1, C2, C5, C6, C7 | AC8
def test_multiple_cancellations_preserve_fifo_order():
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.register("u4")

    er.cancel("u1")
    er.cancel("u2")

    assert er.snapshot()["registered"] == ["u3", "u4"]
    assert er.snapshot()["waitlist"] == []


# Covers C7 | AC15
def test_cancel_registered_user_with_empty_waitlist():
    er = EventRegistration(capacity=2)
    er.register("u1")

    result = er.cancel("u1")

    assert result == OperationResult(
        status=UserStatus("not_found"),
        explanation="registration cancelled: no promotion occurred"
    )
    assert er.snapshot()["registered"] == []
    assert er.snapshot()["waitlist"] == []


# Covers C7 | AC13
def test_invalid_capacity_raises_value_error():
    with pytest.raises(ValueError):
        EventRegistration(-1)


# Covers C7 | input validation edge case
def test_empty_string_user_id_raises_value_error():
    er = EventRegistration(capacity=1)

    with pytest.raises(ValueError):
        er.register("")
