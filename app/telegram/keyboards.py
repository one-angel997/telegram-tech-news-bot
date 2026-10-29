from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_category_keyboard(categories):
    items = list(categories.items())
    rows = []

    for index in range(0, len(items), 2):
        row = []
        for category_id, category_data in items[index:index + 2]:
            row.append(
                InlineKeyboardButton(
                    category_data.get("label", category_id),
                    callback_data=f"category:{category_id}",
                )
            )
        rows.append(row)

    rows.append([InlineKeyboardButton("📰 Tutte", callback_data="category:all")])
    return InlineKeyboardMarkup(rows)


def build_summary_keyboard(entries):
    rows = []
    for index, _ in enumerate(entries[:10]):
        rows.append([
            InlineKeyboardButton(f"Riassunto {index + 1}", callback_data=f"get_summary:{index}")
        ])
    return InlineKeyboardMarkup(rows)
