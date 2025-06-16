from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiExample
)

from .serializers import *

REGISTER_SCHEMA = extend_schema(
    tags=['Аккаунт'],
    summary='Регистрация пользователя',
    description='Создание нового пользователя в системе',
    request={
        'application/json': {
            'example': {
                'username': 'name',
                'email': 'email@mail.ru',
                'password': 'password1234'
            }
        }
    }
)

AUTH_SCHEMA = extend_schema(
        tags=['Аккаунт'],
        summary='Получение токенов доступа',
        description='Возвращает access и refresh токены при успешной аутентификации',
        request={
            'application/json': {
                'example': {
                    'username': 'test',
                    'password': 'test1234'
                }
            }
        }
    )

TOKEN_REFRESH_SCHEMA = extend_schema(
    tags=['Аккаунт'],
    summary='Обновление access токена',
    description='Получение нового access токена по действительному refresh токену',
    request={
        'application/json': {
            'example': {
                'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1MDA1MDIwNywiaWF0IjoxNzQ5NDQ1NDA3LCJqdGkiOiJjNDIyN2RlYjNlMzc0NTNhOGE5NDQ0MjRjMzdhMzY0ZiIsInVzZXJfaWQiOjN9.HAqqv-qTAOq8bIQriuZc8LAXVW-m8Eibcj46C1M-CIk'
            }
        }
    }
)

CLASSES_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=['Классы'],summary='Список классов',
        description='Получение всех классов (их id и названия)'),

    create=extend_schema(
        tags=['Классы'], summary='Создание класса(ов)',
        description='Создание класса(ов) с указанием имени',
        examples=[
            OpenApiExample(
                'Пример создания одного класса',
                value={'name': '1А'},
                request_only=True
            ),
            OpenApiExample(
                'Пример создания нескольких классов',
                value=[
                    {'name': '1А'},
                    {'name': '2Б'}
                ],
                request_only=True
            )
        ]),

    retrieve=extend_schema(
        tags=['Классы'], summary='Получение класса',
        description='Получение имени класса по id'),

    update=extend_schema(
        tags=['Классы'], summary='Обновление класса',
        description='Изменение имени класса по id',
        request={
            'application/json': {
                'example': {
                    'name': '5Г'
                }
            }
        }
    ),
    destroy=extend_schema(
        tags=['Классы'], summary='Удаление класса',
        description='Удаление класса класса по id')
)

STUDENTS_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=['Ученики'],summary='Список учеников',
        description='Получение всех учеников (их id, name, student_id и classroom)'),

    retrieve=extend_schema(
        tags=['Ученики'], summary='Получение ученика',
        description='Получение ученика по id (его id, name, student_id и classroom)'),

    create=extend_schema(
        tags=['Ученики'], summary='Создание ученика(ов) и добавление в класс',
        description='Создание ученика(ов) с указанием имени и id класса (при создании автоматически генерируется 12-значный ID)',
        examples=[
            OpenApiExample(
                'Пример создания одного ученика',
                value={'name': 'Петр',
                       'classroom': 1},
                request_only=True
            ),
            OpenApiExample(
                'Пример создания нескольких учеников',
                value=[
                    {'name': 'Петр',
                    'classroom': 1},
                    {'name': 'Максим',
                     'classroom': 1}
                ],
                request_only=True
            )
        ]),

    update=extend_schema(
        tags=['Ученики'], summary='Изменение данных ученика (полностью)',
        description='Замена информации (имени, класса) ученика по id',
        request={
            'application/json': {
                'example': {
                    'name': 'Марк',
                    'classroom': 2
                }
            }
        },
    ),
    partial_update=extend_schema(
        tags=['Ученики'], summary='Изменение части данных ученика',
        description='Изменение информации (имени и/или класса) ученика по id',
        request={
            'application/json': {
                'example': {
                    'classroom': 1
                }
            }
        }
    ),
    destroy=extend_schema(
        tags=['Ученики'], summary='Удаление ученика',
        description='Удаление ученика по id')
)

TESTS_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=['Тесты'],summary='Получение всех тестов',
        description='Получение всех тестов (их id и title, а также questions_count(вычисляется))'),

    retrieve=extend_schema(
        tags=['Тесты'], summary='Получение теста',
        description='Получение теста по id (его id, title, а также вложенные questions привязанные к test и все answers привязанные к questions)'),

    create=extend_schema(
        tags=['Тесты'], summary='Создание теста',
        description='Создание теста с опциональной вложенностью: вопросы или вопросы с ответами',
        examples=[
            OpenApiExample(
                'Пример создания теста без вопросов',
                value={
                    "title": "Название: тема",
                    "questions" : []
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример создания теста с вопросами, без ответов',
                value={
                    "title": "Название: тема",
                    "questions": [
                        {
                            "text": "Вопрос 1",
                            "question_type": "one",
                            "answers" : []
                        },
                        {
                            "text": "Вопрос 2",
                            "question_type": "multiple",
                            "answers": []
                        },
                        {
                            "text": "Вопрос 3",
                            "question_type": "text",
                            "answers": []
                        }
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример создания теста с вопросами и ответами',
                value={
                    "title": "Название: тема",
                    "questions": [
                        {
                            "text": "Вопрос 1",
                            "question_type": "one",
                            "answers" : [
                                {
                                    "text" : "Ответ 11",
                                    "is_correct" : True
                                },
                                {
                                    "text": "Ответ 12",
                                    "is_correct": False
                                },
                                {
                                    "text": "Ответ 13",
                                    "is_correct": False
                                },
                                {
                                    "text": "Ответ 14",
                                    "is_correct": False
                                },
                            ]
                        },
                        {
                            "text": "Вопрос 2",
                            "question_type": "multiple",
                            "answers": [
                                {
                                    "text" : "Ответ 21",
                                    "is_correct" : True
                                },
                                {
                                    "text": "Ответ 22",
                                    "is_correct": True
                                },
                                {
                                    "text": "Ответ 23",
                                    "is_correct": True
                                },
                                {
                                    "text": "Ответ 24",
                                    "is_correct": False
                                },
                            ]
                        },
                        {
                            "text": "Вопрос 3",
                            "question_type": "true_false",
                            "answers": [
                                {
                                    'text': "Правда",
                                    "is_correct" : True
                                },
                                {
                                    'text': "Лож",
                                    "is_correct": False
                                }
                            ]
                        }
                    ]
                },
                request_only=True
            )
        ]),

    update=extend_schema(
        tags=['Тесты'], summary='Изменение теста (полностью)',
        description='Замена информации теста (title) по id, а также вопросов и ответов к нему',
        request={
            'application/json': {
                'example': {
                    "title": "Новое название: новая тема",
                    "questions": [
                        {
                            "text": "Вопрос 1",
                            "question_type": "one",
                            "answers": [
                                {
                                    "text": "Ответ 11",
                                    "is_correct": True
                                },
                                {
                                    "text": "Ответ 12",
                                    "is_correct": False
                                },
                                {
                                    "text": "Ответ 13",
                                    "is_correct": False
                                },
                                {
                                    "text": "Ответ 14",
                                    "is_correct": False
                                },
                            ]
                        },
                        {
                            "text": "Вопрос 2",
                            "question_type": "multiple",
                            "answers": [
                                {
                                    "text": "Ответ 21",
                                    "is_correct": True
                                },
                                {
                                    "text": "Ответ 22",
                                    "is_correct": True
                                },
                                {
                                    "text": "Ответ 23",
                                    "is_correct": True
                                },
                                {
                                    "text": "Ответ 24",
                                    "is_correct": False
                                },
                            ]
                        },
                        {
                            "text": "Вопрос 3",
                            "question_type": "text",
                            "answers": []
                        }
                    ]
                }
            }
        }
    ),
    partial_update=extend_schema(
        tags=['Тесты'], summary='Изменение части теста (название, вопросы, ответы)',
        description='Изменение информации теста по id, названия и/или вопросов и/или ответов к вопросам (РАБОТАЕТ КАК PUT)',
        # request={
        #     'application/json': {
        #         'example': {
        #             'classroom': 1
        #         }
        #     }
        # }
    ),
    destroy=extend_schema(
        tags=['Тесты'], summary='Удаление теста',
        description='Удаление теста по id (а также вопросов и ответов к ним, каскадно)'),
    clone=extend_schema(
        tags=['Тесты'], summary='Клонирование теста',
        description='Клонирование теста по id (а также вопросов и ответов к ним)')
)

TEST_LAUNCH_SCHEMA = extend_schema_view(
    list=extend_schema(
        tags=['Сессии тестов'],summary='Получение всех сессий',
        description='Получение всех сессий тестов, получим: id, test(id), classrooms([ids]),'
                    ' launched_at(время запуска), expires_at(время окончания), is_active(активна ли сейчас).<br>'
                    ' При данном запросе проверяется не истекло ли время сессии, если истекло, то is_active становится false'),

    retrieve=extend_schema(
        tags=['Сессии тестов'], summary='Получение сессии',
        description='Получение сессии теста по id, получим: id, test(id), classrooms([ids]),'
                    ' launched_at(время запуска), expires_at(время окончания), is_active(активна ли сейчас)'),

    create=extend_schema(
        tags=['Сессии тестов'], summary='Создание сессии',
        description='Запуск сессии с указанием: id теста; класса(ов) (допуск);'
                    ' времени: начала и конца; конца (тогда сессия начнется в момент запуска);'
                    ' не указывать (тогда активен пока в ручную через PATCH не будет задан is_active=false)',
        examples=[
            OpenApiExample(
                'Пример создания сессии без времени окончания',
                value={ 'test': 1,
                        'classrooms': [1]},
                request_only=True
            ),
            OpenApiExample(
                'Пример создания сессии c указанием времени окончания',
                value={
                    'test': 1,
                    'classrooms': [1],
                    'expires_at': "2025-06-07T15:00:00Z"
                },
                request_only=True
            )
        ]),

    update=extend_schema(
        tags=['Сессии тестов'], summary='Изменение сессии (полностью)',
        description='Замена информации сессии по id: класса(ов);'
                    ' времени: начала и конца; конца (тогда сессия начнется в момент запуска);'
                    ' не указывать (тогда активен пока в ручную через PATCH не будет задан is_active=false)',
        request={
            'application/json': {
                'example': {
                    'test': 1,
                    'classrooms': [1],
                    'is_active': True
                }
            }
        }
    ),
    partial_update=extend_schema(
        tags=['Сессии тестов'], summary='Изменение части информации о сессии',
        description='Изменение информации сессии по id: класса(ов); времени (конец / начало и конец / без времени)<br>'
                    'Можно указать is_active=true/false (начать/закончить сессию)',
        request={
            'application/json': {
                'example': {
                    'test': 1,
                    'classrooms': [1],
                    'is_active': False
                }
            }
        }
    ),
    destroy=extend_schema(
        tags=['Сессии тестов'], summary='Удаление сессии',
        description='Удаление записи сессии, вместе с ней удаляются результаты пройденных тестов')
)

GENERATE_TEST_SCHEMA = extend_schema(
        tags=['GigaChat'],
        summary='Запрос к API на генерацию теста',
        description='Тело запроса: topic(тема); question_count(кол-во вопросов);'
                    ' type_distribution (JSON с заданными типами вопросов).<br>'
                    'Реакция: формируется и отправляется запрос с промптом к API - полученный ответ парсится - создается и сохраняется тест',
        request={
            'application/json': {
                'example': {
                    'topic': "Тема теста",
                    'question_count': 5,
                    'type_distribution': {
                        'one': 3,
                        'multiple': 1,
                        'true_false': 1
                    }
                }
            }
        }
    )

SUBMIT_ANSWERS_SCHEMA = extend_schema(
    tags=['Тесты'],
    summary='Отправление выбранных ответов и проверка',
    description='Запрос на запись выбранных ответов учеником с указанием:<br>student_id; test_launch_id;<br>'
                'answers: [] (в который входят эл-ты: question (id вопроса) и массив selected_answers).<br>'
                'Выбранные ответы сохраняются, после чего проверяются и подсчитывается результат прохождения теста в %',
    request={
        'application/json': {
            'example': {
                'student_id': '2ec7ab586713',
                'test_launch_id': 42,
                'answers': [
                    {
                        "question": 101,
                        "selected_answers": [5]
                    },
                    {
                        "question": 102,
                        "selected_answers": [8, 9]
                    }
                ]
            }
        }
    }
)

SESSION_RESULTS_SCHEMA = extend_schema(
    tags=['Статистика и успеваемость'],
    summary='Получение успеваемости по сессии всех учеников',
    description='Получение успеваемости по сессии всех учеников'
)

STUDENT_TEST_ANSWERS_SCHEMA = extend_schema(
    tags=['Статистика и успеваемость'],
    summary='Получение ответов указанных учеником',
    description='Получение ответов указанных учеником, они вложены в тест (со всеми вопросам), также отображены score и completed_at'
)