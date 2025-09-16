import pandas as pd

data = [
    [
        ["Revision", "Full Name", "Email", "Reviewed Date", "Changes Made (If Any)"],
        [
            "1.0",
            "Sarah Thompson",
            "sarah.thompson@cadence.com",
            "2023-06-01",
            "Initial draft of network topology diagram created.",
        ],
        [
            "1.1",
            "Michael Chen",
            "m.chen@cadence.com",
            "2023-12-03",
            "Updated IP addressing scheme and VLAN assignments.",
        ],
        [
            "1.2",
            "Aisha Rahman",
            "aisha.rahman@cadence.com",
            "2024-05-07",
            "No changes. Reviewed and approved existing diagram.",
        ],
        [
            "1.3",
            "Priya Desai",
            "priya.desai@cadence.com",
            "2024-10-15",
            "No changes. Confirmed compliance with updated security policies.",
        ],
    ]
]

df = pd.DataFrame(data[0][1:], columns=data[0][0])
print(df)
