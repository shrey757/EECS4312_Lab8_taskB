## Student Name: Shrey Grover
## Student ID: 219579143

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Kept for compatibility with earlier lab versions."""
    pass


class NotFound(Exception):
    """Kept for compatibility with earlier lab versions."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "not_found"
    position:
      - 1-based waitlist position if waitlisted
      - None otherwise
    """
    state: str
    position: Optional[int] = None


@dataclass(frozen=True)
class OperationResult:
    """
    status:
      - resulting user status after the operation
    explanation:
      - exactly one explanation message when required
      - None for simple successful operations that do not require explanation
    """
    status: UserStatus
    explanation: Optional[str] = None


class EventRegistration:
    """
    Persona-aware event registration system with:
    - fixed capacity
    - FIFO waitlist
    - deterministic behavior
    - duplicate prevention across the whole system
    - explicit edge-case handling
    - short explanations for rejections and promotions
    """

    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 0:
            raise ValueError("capacity must be >= 0")

        self.capacity: int = capacity
        self._registered: List[str] = []
        self._waitlist: List[str] = []

    def register(self, user_id: str) -> OperationResult:
        """
        Register a user.

        Rules:
        - If capacity is available, register the user.
        - Otherwise, place the user in the FIFO waitlist.
        - If the user already exists anywhere in the system, reject the request.
        """
        self._validate_user_id(user_id)

        if user_id in self._registered:
            return OperationResult(
                status=UserStatus("registered"),
                explanation="duplicate registration rejected: user is already registered"
            )

        if user_id in self._waitlist:
            return OperationResult(
                status=UserStatus("waitlisted", self._waitlist.index(user_id) + 1),
                explanation="duplicate registration rejected: user is already waitlisted"
            )

        if len(self._registered) < self.capacity:
            self._registered.append(user_id)
            return OperationResult(status=UserStatus("registered"))

        self._waitlist.append(user_id)
        return OperationResult(
            status=UserStatus("waitlisted", len(self._waitlist))
        )

    def cancel(self, user_id: str) -> OperationResult:
        """
        Cancel a registered or waitlisted user.

        Rules:
        - If the user is registered, remove them.
        - If a waitlist exists and capacity allows, promote the earliest waitlisted user.
        - If the user is waitlisted, remove them and preserve remaining order.
        - If the user is not found, return an explicit not_found outcome.
        """
        self._validate_user_id(user_id)

        if user_id in self._registered:
            self._registered.remove(user_id)

            if self._waitlist and len(self._registered) < self.capacity:
                promoted_user = self._waitlist.pop(0)
                self._registered.append(promoted_user)
                return OperationResult(
                    status=UserStatus("not_found"),
                    explanation=(
                        f"registration cancelled: {promoted_user} was promoted "
                        f"from the waitlist due to the open slot"
                    )
                )

            return OperationResult(
                status=UserStatus("not_found"),
                explanation="registration cancelled: no promotion occurred"
            )

        if user_id in self._waitlist:
            self._waitlist.remove(user_id)
            return OperationResult(
                status=UserStatus("not_found"),
                explanation="waitlist entry cancelled"
            )

        return OperationResult(
            status=UserStatus("not_found"),
            explanation="cancellation rejected: user not found"
        )

    def status(self, user_id: str) -> UserStatus:
        """
        Return the current user status.

        States:
        - registered
        - waitlisted (with 1-based position)
        - not_found
        """
        self._validate_user_id(user_id)

        if user_id in self._registered:
            return UserStatus("registered")

        if user_id in self._waitlist:
            return UserStatus(
                "waitlisted",
                self._waitlist.index(user_id) + 1
            )

        return UserStatus("not_found")

    def snapshot(self) -> dict:
        """
        Return a deterministic snapshot of internal state.
        """
        return {
            "capacity": self.capacity,
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
        }

    def _validate_user_id(self, user_id: str) -> None:
        """
        User IDs are treated as exact, case-sensitive strings.
        """
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a string")
        if user_id.strip() == "":
            raise ValueError("user_id must be a non-empty string")
