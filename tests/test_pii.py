from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "[REDACTED_EMAIL]" in out


def test_scrub_phone_vn() -> None:
    # Test different formats of Vietnamese phone numbers
    assert "[REDACTED_PHONE_VN]" in scrub_text("Call me at 0901234567")
    assert "[REDACTED_PHONE_VN]" in scrub_text("My number is +84 901 234 567")
    assert "[REDACTED_PHONE_VN]" in scrub_text("Contact: 090.123.4567")


def test_scrub_cccd() -> None:
    # Test 12-digit CCCD
    out = scrub_text("Số CCCD của tôi là 012345678901")
    assert "012345678901" not in out
    assert "[REDACTED_CCCD]" in out


def test_scrub_credit_card() -> None:
    # Test credit card numbers with spaces or dashes
    assert "[REDACTED_CREDIT_CARD]" in scrub_text("Card: 1234-5678-9012-3456")
    assert "[REDACTED_CREDIT_CARD]" in scrub_text("Card: 1234 5678 9012 3456")


def test_scrub_passport() -> None:
    # Test Vietnamese passport format (1 letter + 8 digits)
    out = scrub_text("Hộ chiếu: B12345678")
    assert "B12345678" not in out
    assert "[REDACTED_PASSPORT]" in out


def test_scrub_vn_address() -> None:
    # Test address keywords
    assert "[REDACTED_VN_ADDRESS]" in scrub_text("Tôi sống ở Đường Nguyễn Trãi, Quận Thanh Xuân")
    assert "[REDACTED_VN_ADDRESS]" in scrub_text("Địa chỉ: Số 10, Phố Huế, Thành phố Hà Nội")


def test_scrub_mixed_pii() -> None:
    # Test multiple PII types in one string
    text = "Email: test@gmail.com, Phone: 0987654321, Address: Quận 1, TP.HCM"
    out = scrub_text(text)
    assert "[REDACTED_EMAIL]" in out
    assert "[REDACTED_PHONE_VN]" in out
    assert "[REDACTED_VN_ADDRESS]" in out
