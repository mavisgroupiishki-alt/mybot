import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

ADMIN_CHAT_ID = 1112419667

VIDEO_LIBRARY = {
    "Аттестация": {
        "description": "Краткий гайд по процедуре аттестации сотрудников.\nЧто нужно знать руководителю и HR.",
        "video": "https://drive.google.com/uc?export=download&id=1Ztdz4evnkFQF6ceGBvg5FsdBqJu4n8eR",
        "fallback_url": "https://drive.google.com/uc?export=download&id=1Ztdz4evnkFQF6ceGBvg5FsdBqJu4n8eR",
    },
    "Охрана труда": {
        "description": "Основные требования охраны труда.\nИнструктаж, документация, ответственность.",
        "video": "https://example.com/videos/ohrana_truda.mp4",
        "fallback_url": "https://example.com/videos/ohrana_truda.mp4",
    },
    "Пожарная безопасность": {
        "description": "Правила пожарной безопасности на предприятии.\nЧто делать при пожаре.",
        "video": "https://example.com/videos/pozharnaya.mp4",
        "fallback_url": "https://example.com/videos/pozharnaya.mp4",
    },
    "Электробезопасность": {
        "description": "Группы допуска по электробезопасности.\nТребования и порядок присвоения.",
        "video": "https://example.com/videos/electro.mp4",
        "fallback_url": "https://example.com/videos/electro.mp4",
    },
    "Первая помощь": {
        "description": "Алгоритм оказания первой помощи.\nОбязанности работодателя и сотрудников.",
        "video": "https://example.com/videos/pervaya_pomosh.mp4",
        "fallback_url": "https://example.com/videos/pervaya_pomosh.mp4",
    },
}
