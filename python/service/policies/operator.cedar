permit (
    principal is demo::User,
    action,
    resource
) when {
    principal.roles.contains("operator")
};
