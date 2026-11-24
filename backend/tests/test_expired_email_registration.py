import os
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import unittest
import uuid


TEST_DATABASE = Path(tempfile.gettempdir()) / f"eshshop-registration-{uuid.uuid4().hex}.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE}"
os.environ["ENVIRONMENT"] = "development"
os.environ["SMTP_HOST"] = ""
os.environ["SMTP_FROM_EMAIL"] = ""

from fastapi import HTTPException

from app.auth import verify_password
from app.database import SessionLocal, engine
from app.models import Base, EmailVerificationToken, User
from app.routers.buyer_auth import confirm_email_verification, register
from app.schemas import EmailVerificationConfirm, UserRegister


class ExpiredEmailRegistrationTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        engine.dispose()
        TEST_DATABASE.unlink(missing_ok=True)

    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def registration(self, email: str, password: str = "Password123"):
        return register(UserRegister(
            email=email,
            password=password,
            display_name="Test Buyer",
        ), self.db)

    def test_email_can_be_registered_again_only_after_unused_token_expires(self):
        email = "expired-registration@example.test"
        first_response = self.registration(email)
        first_user = self.db.query(User).filter(User.email == email).one()
        first_user_id = first_user.id

        with self.assertRaises(HTTPException) as active_error:
            self.registration(email, "NewPassword123")
        self.assertEqual(active_error.exception.status_code, 400)

        first_token = self.db.query(EmailVerificationToken).filter_by(user_id=first_user_id).one()
        first_token.expires_at = datetime.utcnow() - timedelta(seconds=1)
        self.db.commit()

        second_response = self.registration(email, "NewPassword123")
        recycled_user = self.db.query(User).filter(User.email == email).one()
        self.assertEqual(recycled_user.id, first_user_id)
        self.assertTrue(verify_password("NewPassword123", recycled_user.password_hash))
        self.assertEqual(
            self.db.query(EmailVerificationToken).filter_by(user_id=first_user_id).count(),
            1,
        )
        self.assertTrue(second_response["verification_required"])

        confirm_email_verification(
            EmailVerificationConfirm(token=second_response["email_verification_token"]),
            self.db,
        )
        with self.assertRaises(HTTPException) as verified_error:
            self.registration(email, "ThirdPassword123")
        self.assertEqual(verified_error.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
