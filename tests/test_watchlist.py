"""
tests/test_watchlist.py — CineLog

Tests for the watchlist service.
"""

import pytest
from models import WatchlistEntry
from services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    AlreadyInWatchlistError,
    NotInWatchlistError,
    FilmNotFoundError,
)


# ── Basic add ───────────────────────────────────────────────────────────────

def test_add_to_watchlist_creates_entry(app, sample_user, sample_film):
    """
    Adding a valid film should create a WatchlistEntry in the database.
    """
    with app.app_context():
        entry = add_to_watchlist(user_id=sample_user, film_id=sample_film)

        assert entry is not None
        assert entry.user_id == sample_user
        assert entry.film_id == sample_film

        # Verify it persisted
        in_db = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first()
        assert in_db is not None

# ── Deduplication ────────────────────────────────────────────────────────────

def test_add_to_watchlist_duplicate_raises(app, sample_user, sample_film):
    """
    Adding the same film twice should raise AlreadyInWatchlistError and
    keep the watchlist from creating duplicate entries.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)

        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 1


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film that does not exist should raise FilmNotFoundError.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)


def test_remove_from_watchlist_deletes_entry(app, sample_user, sample_film):
    """
    Removing a saved film should delete the matching WatchlistEntry.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        result = remove_from_watchlist(user_id=sample_user, film_id=sample_film)

        assert result is True
        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 0


def test_remove_from_watchlist_missing_entry_raises(app, sample_user, sample_film):
    """
    Removing a film that was never added should raise NotInWatchlistError.
    """
    with app.app_context():
        with pytest.raises(NotInWatchlistError):
            remove_from_watchlist(user_id=sample_user, film_id=sample_film)