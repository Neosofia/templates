permit (
    principal is demo::Patient,
    action == Action::"document:read",
    resource is demo::Document
) when {
    resource.owner == principal
};permit (
    principal is demo::Clinician,
    action == Action::"document:read",
    resource is demo::Document
) when {
    ["physician", "nurse_practitioner", "physician_assistant", "registered_nurse"].contains(principal.role) &&
    resource.clinic_id == principal.clinic_id
};permit (
    principal is demo::Clinician,
    action == Action::"document:delete",
    resource is demo::Document
) when {
    principal.role == "admin"
};