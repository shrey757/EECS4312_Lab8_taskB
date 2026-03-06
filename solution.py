## Student Name: Shrey Grover
## Student ID: 219579143

"""
Task B: Event Registration with Waitlist (Stub)
In this lab, you will design and implement an Event Registration with Waitlist system using an LLM assistant as your primary programming collaborator.
You are asked to implement a Python module that manages registration for a single event with a fixed capacity.
The system must:
• Accept a fixed capacity.
• Register users until capacity is reached.
• Place additional users into a FIFO waitlist.
• Automatically promote the earliest waitlisted user when a registered user cancels.
• Prevent duplicate registrations.
• Allow users to query their current status.

The system must ensure that:
• The number of registered users never exceeds capacity.
• Waitlist ordering preserves FIFO behavior.
• Promotions occur deterministically under identical operation sequences.

The module must preserve the following invariants:
• A user may not appear more than once in the system.
• A user may not simultaneously exist in multiple states.
• The system state must remain consistent after every operation.

The system must correctly handle non-trivial scenarios such as:
• Multiple cancellations in sequence.
• Users attempting to re-register after canceling.
• Waitlisted users canceling before promotion.
• Capacity equal to zero.
• Simultaneous or rapid consecutive operations.
• Queries during state transitions.

The output consists of the updated registration state and ordered lists of registered and waitlisted users after each operation.
"""

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation (if required by handout)."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Event registration system with:
    - fixed capacity
    - FIFO waitlist
    - automatic promotion on cancellation
    - duplicate prevention
    - deterministic behavior
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 0:
            raise ValueError("capacity must be >= 0")

        self.capacity: int = capacity
        self._registered: List[str] = []
        self._waitlist: List[str] = []

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists (registered or waitlisted)
        """
        self._validate_user_id(user_id)

        if user_id in self._registered or user_id in self._waitlist:
            raise DuplicateRequest(f"user '{user_id}' already exists in the system")

        if len(self._registered) < self.capacity:
            self._registered.append(user_id)
            return UserStatus(state="registered", position=None)

        self._waitlist.append(user_id)
        return UserStatus(state="waitlisted", position=len(self._waitlist))

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user (if any)
          - if waitlisted -> remove from waitlist
          - if user not found -> raise NotFound
        """
        self._validate_user_id(user_id)

        if user_id in self._registered:
            self._registered.remove(user_id)

            if self._waitlist:
                promoted_user = self._waitlist.pop(0)
                self._registered.append(promoted_user)
            return

        if user_id in self._waitlist:
            self._waitlist.remove(user_id)
            return

        raise NotFound(f"user '{user_id}' not found in the system")

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        """
        self._validate_user_id(user_id)

        if user_id in self._registered:
            return UserStatus(state="registered", position=None)

        if user_id in self._waitlist:
            return UserStatus(
                state="waitlisted",
                position=self._waitlist.index(user_id) + 1
            )

        return UserStatus(state="none", position=None)

    def snapshot(self) -> dict:
        """
        Return a deterministic snapshot of internal state.
        """
        return {
            "capacity": self.capacity,
            "registered": list(self._registered),
            "waitlisted": list(self._waitlist),
        }

    def _validate_user_id(self, user_id: str) -> None:
        """Validate user identifier."""
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a string")
        if user_id.strip() == "":
            raise ValueError("user_id must be a non-empty string")
