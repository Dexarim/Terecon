import PyPDF2
import pandas as pd
import re
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import torch
from typing import Dict, List, Any

# Инициализация модели DeBERTa
model_name = "microsoft/deberta-v3-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)  # 2 метки: Подходит / Не подходит
nlp = pipeline("text-classification", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

# Функция оценки кандидата с использованием DeBERTa
def evaluate_candidate_with_model(resume_text: str, job_description: str) -> str:
    prompt = f"""
    Оцените, подходит ли кандидат для должности.
    Резюме: {resume_text}
    Описание должности: {job_description}
    """
    result = nlp(prompt)
    print(result)
    return "Подходит" if result[0]['label'] == 'LABEL_1' else "Не подходит"

def extract_info(text: str) -> Dict[str, Any]:
    text = text.replace('\n', ' ').strip()
    data = {}

    # 1. Извлекаем ФИО
    name_match = re.search(r'([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)', text)
    data["Name"] = f"{name_match.group(1)} {name_match.group(2)}" if name_match else 'N/A'

    # 2. Извлекаем пол и возраст
    gender_age_match = re.search(r'(Мужчина|Женщина)[,]?\s*(\d{1,2})\s*(лет|года|год)?', text)
    data["Gender"] = gender_age_match.group(1) if gender_age_match else 'N/A'
    data["Age"] = gender_age_match.group(2) if gender_age_match else 'N/A'

    # 3. Извлекаем номер телефона
    phone_match = re.search(r'(\+7\s?\(?\d{3}\)?\s?\d{3}[\s-]?\d{2}[\s-]?\d{2})', text)
    data["Phone"] = phone_match.group(1) if phone_match else 'N/A'

    # 4. Извлекаем почту
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    data["Email"] = email_match.group(0) if email_match else 'N/A'

    # 5. Извлекаем желаемую должность
    desired_position_match = re.search(r'Желаемая должность и зарплата\s*([\s\S]+?)\s*Специализации:', text)
    data["Desired Position"] = desired_position_match.group(1).strip() if desired_position_match else 'N/A'

    # 6. Извлекаем навыки
    skills_match = re.search(r'Навыки\s*([\s\S]+?)\s*Резюме', text)
    data["Skills"] = skills_match.group(1).strip() if skills_match else ''

    # 7. Извлекаем опыт работы
    experience_match = re.findall(r'(\d{1,2})\s*(лет|года|год)\s*в\s*должности\s*([А-ЯЁа-яё\s]+)', text)
    data["Experience"] = [int(exp[0]) for exp in experience_match] if experience_match else []

    return data

def pdf_to_text(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.strip()

def extract_data_from_pdf(pdf_path: str) -> Dict[str, Any]:
    text = pdf_to_text(pdf_path)
    return extract_info(text)

def save_to_csv(data: Dict[str, Any], csv_path: str) -> None:
    df = pd.DataFrame([data])
    try:
        existing_df = pd.read_csv(csv_path, on_bad_lines='skip')
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        existing_df = pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"Ошибка при чтении CSV файла: {e}")
        existing_df = pd.DataFrame()

    df.to_csv(csv_path, index=False)

def calculate_score(row: Dict[str, Any], job_description: str, desired_positions: List[str], required_skills: List[str]) -> int:
    score = 0
    if row['Desired Position'] in desired_positions:
        score += 10
    if any(skill in row['Skills'] for skill in required_skills):
        score += 5
    
    # Проверяем, что 'Experience' - это список, и суммируем его
    if isinstance(row['Experience'], list):
        score += sum(row['Experience'])  # Суммируем опыт
    else:
        score += 0  # Или вы можете установить score += row['Experience'] если хотите обработать это иначе

    return score

def add_scores_to_csv(csv_path: str, job_description: str, desired_positions: List[str], required_skills: List[str]) -> None:
    df = pd.read_csv(csv_path)

    # Обработка оценки кандидатов
    df['AI Evaluation'] = df.apply(lambda row: evaluate_candidate_with_model(row['Skills'], job_description), axis=1)

    # Вычисление баллов
    df['Score'] = df.apply(lambda row: calculate_score(row, job_description, desired_positions, required_skills), axis=1)

    # Сохранение обновленного CSV
    df.to_csv(csv_path, index=False)
    
    
def main(pdf_path: str, csv_path: str, job_description: str, desired_positions: List[str], required_skills: List[str]):
    data = extract_data_from_pdf(pdf_path)
    save_to_csv(data, csv_path)
    add_scores_to_csv(csv_path, job_description, desired_positions, required_skills)


if __name__ == "__main__":
    # Ввод пути к PDF файлу
    pdf_path = 'data/pdf/rez4.pdf'
    
    # Ввод пути к CSV файлу
    csv_path = 'data/csv/output.csv'
    
    # Ввод описания вакансии
    job_description = input("Введите описание вакансии: ")
    
    # Ввод желаемых должностей
    desired_positions_input = input("Введите желаемые должности (через запятую): ")
    desired_positions = [position.strip() for position in desired_positions_input.split(',')]
    
    # Ввод требуемых навыков
    required_skills_input = input("Введите требуемые навыки (через запятую): ")
    required_skills = [skill.strip() for skill in required_skills_input.split(',')]
    
    # Запуск основной функции
    main(pdf_path, csv_path, job_description, desired_positions, required_skills)