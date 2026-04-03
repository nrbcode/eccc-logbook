CONTROL_MEASURES = [
    'Safe access and egress',
    'Appropriate training',
    'Correct PPE',
    'Lighting levels appropriate',
    'Tidy work area',
    'Adequate natural ventilation.',
    'Tools are safe and ready for use.',
    'Due consideration to other groups',
]

CONTROLS_ACTIVITIES = {
    'Safe access and egress to the work area.': ["drill", "jackhammer", "hand-grinder"],
    'Appropriate training.': ["drill", "jackhammer", "hand-grinder", "floor-grinder"],
    'Correct Personal Protective Equipment (PPE).': ["drill", "jackhammer", "hand-grinder", "floor-grinder"],
    'Lighting levels appropriate for work tasks.': ["drill", "jackhammer", "hand-grinder", "floor-grinder"],
    'Tidy work area.': ["drill", "hand-grinder", "floor-grinder"],
    'Adequate natural ventilation.': ["jackhammer", "hand-grinder", "floor-grinder"],
    'Tools are safe and ready for use.': ["drill", "jackhammer", "hand-grinder", "floor-grinder"],
    'Due consideration has been given to the work of other groups in the vicinity.': ["jackhammer", "hand-grinder", "floor-grinder"]
    }
    

ACTIVITIES_CONTROLS = {
    "drill": [
        "Safe access and egress to the work area.",
        "Appropriate training.",
        "Correct Personal Protective Equipment (PPE).",
        "Lighting levels appropriate for work tasks.",
        "Tidy work area.",
        "Adequate natural ventilation.",
        "Tools are safe and ready for use.",
        "Due consideration has been given to the work of other groups in the vicinity."
        ],
    "jackhammer": [
        "Safe access and egress to the work area.",
        "Appropriate training.",
        "Correct Personal Protective Equipment (PPE).",
        "Lighting levels appropriate for work tasks.",
        "Tools are safe and ready for use.",
        "Due consideration has been given to the work of other groups in the vicinity."
        ],
    "handgrinder": [
        "Safe access and egress to the work area.",
        "Appropriate training.",
        "Correct Personal Protective Equipment (PPE).",
        "Lighting levels appropriate for work tasks.",
        "Tidy work area.",
        "Adequate natural ventilation.",
        "Tools are safe and ready for use.",
        "Due consideration has been given to the work of other groups in the vicinity."
        ],
    "floorgrinder": [
        "Safe access and egress to the work area.",
        "Appropriate training.",
        "Correct Personal Protective Equipment (PPE).",
        "Lighting levels appropriate for work tasks.",
        "Tidy work area.",
        "Adequate natural ventilation.",
        "Tools are safe and ready for use.",
        "Due consideration has been given to the work of other groups in the vicinity."
        ]
}
