// Allow operator actors full access to all demo service actions and resources.
permit (
    principal is demo::User,
    action,
    resource
) when {
    principal.actors.contains("operator")
};
