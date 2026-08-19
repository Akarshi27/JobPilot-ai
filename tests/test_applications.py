from backend.services.application_providers import ManualApplicationProvider


def test_unsupported_application_provider_requires_manual_action():
    result = ManualApplicationProvider().submit_application({"url": "https://internshala.com/job/detail/test-application"})
    assert result.status == "manual_required"
    assert result.external_application_id is None