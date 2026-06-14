// Allow patients to read documents they own.
permit (
    principal is demo::Patient,
    action == Action::"document:read",
    resource is demo::Document
) when {
    resource.owner == principal
};

// Allow clinical staff at the same clinic to read clinic documents.
permit (
    principal is demo::Clinician,
    action == Action::"document:read",
    resource is demo::Document
) when {
    ["physician", "nurse_practitioner", "physician_assistant", "registered_nurse"].contains(principal.role) &&
    resource.clinic_id == principal.clinic_id
};

// Allow clinic admin clinicians to delete documents at their clinic.
permit (
    principal is demo::Clinician,
    action == Action::"document:delete",
    resource is demo::Document
) when {
    principal.role == "admin"
};
