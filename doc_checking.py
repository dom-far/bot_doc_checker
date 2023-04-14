import docx


def _get_info_of_misstakes(result: dict) -> str:
    if list(filter(lambda key: key == False, result)):
        if len(result['text']) > 50:
            result['text'] = result['text'][:50] + "..."
        outputText = f"В абзаце {result['text']} найдены следующие ошибки:\n"
        if not result["style_font"]:
            outputText += "• не выбран необходимый шрифт\n"
        if not result["font_size"]:
            outputText += "• неверный размер шрифта\n"
        if not result["alignment"]:
            outputText += "• текст не выровнен по ширине\n"
        if not result["first_line_indent"]:
            outputText += "• неверный абзацный отступ\n"
        if not result["line_spacing"]:
            outputText += "• неверный размер межстрочного интервала\n"
        return outputText
    else:
        return False


def check_paragraph(paragraph) -> dict:
    text = ""
    result = {"style_font": True, "font_size": True, 
              "alignment": True, "first_line_indent": True, 
              "line_spacing": True, 
              "text": ""}
    for run in paragraph.runs:
        text += run.text
    result["text"] = text
    if paragraph.style.font.name not in ('Times New Roman', None):
        result["style_font"] = False
    if paragraph.style.font.size != docx.shared.Pt(14):
        result["font_size"] = False
    if paragraph.alignment != docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY:
        result["alignment"] = False
    if paragraph.style.paragraph_format.first_line_indent != docx.shared.Pt(12.7):
        result["first_line_indent"] = False
    if paragraph.style.paragraph_format.line_spacing not in (docx.enum.text.WD_LINE_SPACING.SINGLE, 
                                                docx.enum.text.WD_LINE_SPACING.ONE_POINT_FIVE,
                                                docx.enum.text.WD_LINE_SPACING.DOUBLE):
        result["line_spacing"] = False
    return result


def check(path_file: str) -> str:
    resultOfCheck = ""
    doc = docx.Document(path_file)
    for paragraph in doc.paragraphs:
        misstakes = _get_info_of_misstakes(check_paragraph(paragraph))
        if misstakes:
            resultOfCheck += misstakes + "\n"
    if not resultOfCheck:
        resultOfCheck = "Ошибок не найдено"
    return resultOfCheck