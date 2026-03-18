from app.core.roles import UserRole

role_permissions = {

    UserRole.ADMIN: [
        "view_all",
        "ask_questions",
        "manage_users"
    ],

    UserRole.RECTOR: [
        "view_all",
        "ask_questions",
        "manage_users"
    ],

    UserRole.DECANO: [
        "view_faculty_all",
        "ask_questions"
    ],

    UserRole.DIRECTOR: [
        "view_program_all",
        "ask_questions"
    ],

    UserRole.DOCENTE: [
        "academic_query"
    ],

    UserRole.ESTUDIANTE: [
        "basic_query"
    ]
}

def has_permission(user_role: UserRole, permission: str):
    role_permissions = role_permissions.get(user_role, [])
    return permission in role_permissions
