permit (
    principal is demo::User,
    action,
    resource
) when {
    principal.actors.contains("operator")
};
