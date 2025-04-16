# Итоговый проект «Фудграм»

«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Как запустить проект:

**Клонировать репозиторий**:

```
git clone https://github.com/VitalinaAndreevna/foodgram-st.git
```

**Перейти в директорию backend\foodgram:**

```
cd .\backend\foodgram
```

**Создать файл .env и заполнить:**

```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
USE_SQLITE=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
DB_USER=foodgram_user
DB_PASSWORD=foodgram_password
DB_HOST=postgres
DB_PORT=5432
```

**Перейти в директорию infra и запустить docker-compose:**

```
cd ..\infra
```

```
docker-compose up -d
```

## Список контейнеров:

 - foodgram-front

 - foodgram-db

 - foodgram-backend

 - foodgram-proxy


## Созданные учётные записи:

 - **Админ: Главный Админ**

    Почта: admin@ya.ru

    Пароль: Main_Admin_007
        
 - **Пользователь: Кирилл Соломин**

    Почта: kirrsolo@ya.ru

    Пароль: Kirill_the_best_1

 - **Пользователь: Мелисса Грасc**

    Почта: melissa@ya.ru

    Пароль: Lemongrass_Mel

 - **Пользователь: Оксана Петушкова**

    Почта: oxy@ya.ru

    Пароль: Oxy_n0t_Miron

*P.S. Пользователи имеют несколько рецептов (но не пытайтесь по ним готовить, ингридиенты случайны). Все остальные необходимые команды уже прописаны в Dockerfile.*

## Об авторе:
Обычный студент 4 курса
Ерохина Виталина Андреевна