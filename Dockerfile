FROM python:3.8

WORKDIR /djangoProject

# Gereksinimler dosyasını kopyalayıp yüklemeleri yapalım
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Tüm dosyaları çalışma dizinine kopyala
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver"]
