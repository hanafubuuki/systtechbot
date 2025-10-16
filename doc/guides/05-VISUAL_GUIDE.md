# Визуальный гайд

**Цель:** Понять проект через визуализацию с разных точек зрения.

---

## 1. 🏗️ Системная архитектура

### Трёхслойная архитектура

```mermaid
graph TB
    subgraph Users["👥 Пользователи"]
        U1[Telegram User 1]
        U2[Telegram User 2]
        U3[Telegram User N]
    end

    subgraph Presentation["🎨 Presentation Layer"]
        direction LR
        CMD[commands.py<br/>━━━━━━━━━<br/>/start /help<br/>/clear /role]
        MSG[messages.py<br/>━━━━━━━━━<br/>text handler]
    end

    subgraph Business["⚙️ Business Logic Layer"]
        direction LR
        CTX[context.py<br/>━━━━━━━━━<br/>In-Memory Store<br/>user_contexts dict]
        LLM[llm.py<br/>━━━━━━━━━<br/>OpenAI Client<br/>Singleton]
        ROLES[prompts.py<br/>━━━━━━━━━<br/>System Prompts]
    end

    subgraph External["🌐 External Services"]
        TG[Telegram Bot API<br/>Long Polling]
        AI[OpenAI/OpenRouter API<br/>Chat Completions]
    end

    U1 & U2 & U3 -->|messages| TG
    TG -->|updates| CMD
    TG -->|updates| MSG

    CMD -->|clear_context| CTX
    CMD -->|get prompts| ROLES

    MSG -->|get/save context| CTX
    MSG -->|request| LLM
    MSG -->|get prompts| ROLES

    LLM -->|API call| AI

    MSG & CMD -->|response| TG
    TG -->|reply| U1 & U2 & U3

    style Users fill:#1a202c,stroke:#805ad5,stroke-width:3px,color:#fff
    style Presentation fill:#1a202c,stroke:#3182ce,stroke-width:3px,color:#fff
    style Business fill:#1a202c,stroke:#38a169,stroke-width:3px,color:#fff
    style External fill:#1a202c,stroke:#dd6b20,stroke-width:3px,color:#fff

    style CMD fill:#2d3748,stroke:#63b3ed,stroke-width:2px,color:#fff
    style MSG fill:#2d3748,stroke:#63b3ed,stroke-width:2px,color:#fff
    style CTX fill:#2d3748,stroke:#68d391,stroke-width:2px,color:#fff
    style LLM fill:#2d3748,stroke:#68d391,stroke-width:2px,color:#fff
    style ROLES fill:#2d3748,stroke:#68d391,stroke-width:2px,color:#fff
    style TG fill:#2d3748,stroke:#f6ad55,stroke-width:2px,color:#fff
    style AI fill:#2d3748,stroke:#f6ad55,stroke-width:2px,color:#fff
```

---

## 2. 💬 Поток обработки сообщения

### Полный lifecycle от пользователя до ответа

```mermaid
sequenceDiagram
    autonumber

    actor User as 👤 Пользователь
    participant TG as 🤖 Telegram Bot
    participant Handler as handlers/messages
    participant Context as services/context
    participant Prompts as roles/prompts
    participant LLM as services/llm
    participant OpenAI as ☁️ OpenAI API

    rect rgb(26, 32, 44)
    Note over User,OpenAI: Начало диалога
    User->>TG: "Привет!"
    TG->>Handler: Message(text="Привет!")
    end

    rect rgb(26, 32, 44)
    Note over Handler,Context: Получение контекста
    Handler->>Context: get_context(user_id, chat_id)
    Context-->>Handler: {messages: [], user_name: None}
    end

    rect rgb(26, 32, 44)
    Note over Handler,Prompts: Инициализация контекста
    Handler->>Prompts: get_system_prompt(user_name)
    Prompts-->>Handler: "Ты — AI-ассистент..."
    Handler->>Handler: Добавить system prompt
    Handler->>Handler: Добавить user message
    end

    rect rgb(26, 32, 44)
    Note over Handler,Context: Усечение контекста
    Handler->>Context: trim_context(messages, max=10)
    Context-->>Handler: trimmed messages
    end

    rect rgb(26, 32, 44)
    Note over Handler,OpenAI: Запрос к LLM
    Handler->>TG: send_chat_action("typing")
    Handler->>LLM: get_llm_response(messages, config)
    LLM->>OpenAI: chat.completions.create()
    OpenAI-->>LLM: "Привет! Чем могу помочь?"
    LLM-->>Handler: response
    end

    rect rgb(26, 32, 44)
    Note over Handler,Context: Сохранение результата
    Handler->>Handler: Добавить assistant response
    Handler->>Context: save_context(user_id, chat_id, messages)
    Context->>Context: user_contexts[(id, chat)] = {...}
    end

    rect rgb(26, 32, 44)
    Note over Handler,User: Отправка ответа
    Handler->>TG: answer("Привет! Чем могу помочь?")
    TG->>User: "Привет! Чем могу помочь?"
    end

    Note over User,OpenAI: Диалог продолжается...
```

---

## 3. 🗂️ Структура проекта

### Файловая организация

```mermaid
graph TD
    ROOT[systtechbot/]

    subgraph Entry["📍 Entry Point"]
        BOT[bot.py<br/>━━━━━━━━━<br/>main function<br/>aiogram setup<br/>logging config]
    end

    subgraph Config["⚙️ Configuration"]
        CFG[config.py<br/>━━━━━━━━━<br/>Config dataclass<br/>load_config]
        CONST[constants.py<br/>━━━━━━━━━<br/>MessageRole enum]
        TYPES[message_types.py<br/>━━━━━━━━━<br/>Message TypedDict]
    end

    subgraph Handlers["🎨 Handlers Layer"]
        HCMD[commands.py<br/>━━━━━━━━━<br/>4 commands<br/>Router]
        HMSG[messages.py<br/>━━━━━━━━━<br/>text handler<br/>Router]
    end

    subgraph Services["⚙️ Services Layer"]
        CTX[context.py<br/>━━━━━━━━━<br/>user_contexts dict<br/>CRUD operations]
        LLM[llm.py<br/>━━━━━━━━━<br/>AsyncOpenAI<br/>singleton pattern]
    end

    subgraph Roles["🎭 Roles"]
        PRMPT[prompts.py<br/>━━━━━━━━━<br/>DEFAULT_SYSTEM_PROMPT<br/>ROLE_INFO]
    end

    subgraph Tests["🧪 Tests"]
        TCMD[test_commands.py]
        TCTX[test_context.py]
        TLLM[test_llm.py]
        TPRM[test_prompts.py]
        TCFG[test_config.py]
        THDL[test_handlers.py]
    end

    subgraph Docs["📚 Documentation"]
        GUIDES[guides/<br/>━━━━━━━━━<br/>01-04 гайды]
        VISION[vision.md]
        TASK[tasklist.md]
        ADR[adrs/]
    end

    ROOT --> BOT
    ROOT --> Config
    ROOT --> Handlers
    ROOT --> Services
    ROOT --> Roles
    ROOT --> Tests
    ROOT --> Docs

    BOT -.depends.-> CFG
    BOT -.depends.-> HCMD
    BOT -.depends.-> HMSG

    HMSG -.depends.-> CTX
    HMSG -.depends.-> LLM
    HMSG -.depends.-> PRMPT
    HMSG -.depends.-> CONST

    HCMD -.depends.-> CTX
    HCMD -.depends.-> PRMPT

    LLM -.depends.-> CFG
    CTX -.depends.-> CONST
    CTX -.depends.-> TYPES

    style ROOT fill:#1a202c,stroke:#805ad5,stroke-width:3px,color:#fff
    style Entry fill:#2d3748,stroke:#9f7aea,stroke-width:2px,color:#fff
    style Config fill:#2d3748,stroke:#4299e1,stroke-width:2px,color:#fff
    style Handlers fill:#2d3748,stroke:#48bb78,stroke-width:2px,color:#fff
    style Services fill:#2d3748,stroke:#ed8936,stroke-width:2px,color:#fff
    style Roles fill:#2d3748,stroke:#f6ad55,stroke-width:2px,color:#fff
    style Tests fill:#2d3748,stroke:#9ae6b4,stroke-width:2px,color:#fff
    style Docs fill:#2d3748,stroke:#63b3ed,stroke-width:2px,color:#fff
```

---

## 4. 🔄 Жизненный цикл контекста

### State diagram контекста диалога

```mermaid
stateDiagram-v2
    [*] --> NoContext: Новый пользователь

    state NoContext {
        [*] --> Empty
        Empty: 🆕 Контекст отсутствует
    }

    NoContext --> Creating: Первое сообщение

    state Creating {
        [*] --> AddSystem
        AddSystem: Добавить system prompt
        AddSystem --> AddUser: +user_name если есть
        AddUser --> Ready
        Ready: Контекст готов
    }

    Creating --> Active

    state Active {
        [*] --> DialogRunning
        DialogRunning: 💬 Диалог активен
        DialogRunning: messages: 1-11 шт
        DialogRunning: user_name: сохранён
        DialogRunning: last_activity: обновляется
    }

    Active --> Active: Продолжение диалога\n(+user msg, +assistant msg)

    Active --> NeedsTrim: len(messages) > max+1

    state NeedsTrim {
        [*] --> Trimming
        Trimming: 📏 Усечение контекста
        Trimming: Сохранить system prompt
        Trimming: +последние max сообщений
        Trimming --> Trimmed
        Trimmed: 11 сообщений\n(1 system + 10 dialog)
    }

    NeedsTrim --> Active: Контекст усечён

    Active --> Cleared: Команда /clear

    state Cleared {
        [*] --> Deleted
        Deleted: 🗑️ Контекст удалён
        Deleted: user_contexts.pop((id, chat))
    }

    Cleared --> NoContext: Контекст очищен

    Active --> Lost: Рестарт бота
    NoContext --> Lost: Рестарт бота
    NeedsTrim --> Lost: Рестарт бота

    state Lost {
        [*] --> InMemoryLost
        InMemoryLost: ⚠️ Данные потеряны
        InMemoryLost: In-memory storage
    }

    Lost --> [*]

    note right of Active
        Пример структуры:
        {
          "messages": [...],
          "user_name": "Иван",
          "last_activity": datetime
        }
    end note

    note right of NeedsTrim
        trim_context() всегда
        сохраняет system prompt
    end note
```

---

## 5. 📊 Модель данных

### Class diagram со связями

```mermaid
classDiagram
    class Config {
        +string telegram_token ⚠️
        +string openai_api_key ⚠️
        +string openai_base_url
        +string openai_model
        +int max_tokens
        +float temperature
        +int max_context_messages
        +int openai_timeout
        +load_config() Config
    }

    class MessageRole {
        <<enumeration>>
        +SYSTEM = "system"
        +USER = "user"
        +ASSISTANT = "assistant"
    }

    class Message {
        <<TypedDict>>
        +string role
        +string content
    }

    class UserContext {
        +list~Message~ messages
        +string|null user_name
        +datetime last_activity
    }

    class ContextManager {
        +dict user_contexts
        +get_context(user_id, chat_id) dict
        +save_context(user_id, chat_id, messages, user_name) void
        +clear_context(user_id, chat_id) void
        +trim_context(messages, max_messages) list
    }

    class LLMService {
        -dict _client_cache
        -_get_or_create_client(config) AsyncOpenAI
        +get_llm_response(messages, config) string
    }

    class CommandHandler {
        +router Router
        +cmd_start(message) void
        +cmd_help(message) void
        +cmd_clear(message) void
        +cmd_role(message) void
    }

    class MessageHandler {
        +router Router
        +handle_message(message) void
    }

    class PromptsService {
        +DEFAULT_SYSTEM_PROMPT string
        +ROLE_INFO string
        +get_system_prompt(user_name) string
    }

    Message --> MessageRole: использует
    UserContext o-- Message: содержит много
    ContextManager --> UserContext: управляет
    LLMService --> Config: использует
    LLMService --> Message: обрабатывает
    MessageHandler --> ContextManager: вызывает
    MessageHandler --> LLMService: вызывает
    MessageHandler --> PromptsService: использует
    CommandHandler --> ContextManager: вызывает
    CommandHandler --> PromptsService: использует

    note for Config "⚠️ Обязательные параметры\nиз .env файла"
    note for Message "Формат OpenAI API\nChat Completions"
    note for UserContext "In-memory хранение\nключ: (user_id, chat_id)"
    note for LLMService "Singleton pattern\nдля OpenAI клиента"
```

---

## 6. 🔁 Developer Workflow

### Процесс разработки с TDD

```mermaid
flowchart TD
    Start([💡 Новая задача]) --> Branch[git checkout -b feature/...]

    Branch --> Red[🔴 RED Phase<br/>━━━━━━━━━<br/>Написать failing test]
    Red --> RunTest1{pytest -x}

    RunTest1 -->|❌ FAIL| GoodRed[✅ Ожидаемо]
    RunTest1 -->|✅ PASS| BadRed[❌ Тест некорректен]
    BadRed --> Red

    GoodRed --> Green[🟢 GREEN Phase<br/>━━━━━━━━━<br/>Минимальная реализация]

    Green --> RunTest2{pytest -x}
    RunTest2 -->|❌ FAIL| Green
    RunTest2 -->|✅ PASS| GoodGreen[✅ Тест прошёл]

    GoodGreen --> Refactor[🔵 REFACTOR Phase<br/>━━━━━━━━━<br/>Улучшить код]

    Refactor --> Quality{make quality}

    Quality -->|❌ Format| FixFormat[make format]
    FixFormat --> Quality

    Quality -->|❌ Lint| FixLint[Исправить ruff errors]
    FixLint --> Quality

    Quality -->|❌ Types| FixTypes[Исправить mypy errors]
    FixTypes --> Quality

    Quality -->|❌ Tests| FixTests[Исправить тесты]
    FixTests --> Quality

    Quality -->|✅ All Pass| Manual[🧪 Ручное тестирование<br/>━━━━━━━━━<br/>Проверка в Telegram]

    Manual --> Commit[git commit -m 'feat: ...']
    Commit --> Push[git push origin feature/...]

    Push --> Done([✅ Готово к PR])

    style Start fill:#1a202c,stroke:#805ad5,stroke-width:3px,color:#fff
    style Red fill:#2d3748,stroke:#fc8181,stroke-width:2px,color:#fff
    style Green fill:#2d3748,stroke:#68d391,stroke-width:2px,color:#fff
    style Refactor fill:#2d3748,stroke:#63b3ed,stroke-width:2px,color:#fff
    style Quality fill:#2d3748,stroke:#f6ad55,stroke-width:2px,color:#fff
    style Manual fill:#2d3748,stroke:#9f7aea,stroke-width:2px,color:#fff
    style Done fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#fff
```

---

## 7. ⚡ Обработка команд vs сообщений

### Маршрутизация в aiogram

```mermaid
flowchart LR
    TG[Telegram Update] --> DP{Dispatcher<br/>aiogram}

    DP -->|Command| CmdRouter[Command Router<br/>handlers/commands]
    DP -->|Text| MsgRouter[Message Router<br/>handlers/messages]

    CmdRouter --> Start{/start?}
    CmdRouter --> Help{/help?}
    CmdRouter --> Clear{/clear?}
    CmdRouter --> Role{/role?}

    Start -->|Yes| StartHandler[cmd_start<br/>━━━━━━━━━<br/>Приветствие]
    Help -->|Yes| HelpHandler[cmd_help<br/>━━━━━━━━━<br/>Список команд]
    Clear -->|Yes| ClearHandler[cmd_clear<br/>━━━━━━━━━<br/>clear_context]
    Role -->|Yes| RoleHandler[cmd_role<br/>━━━━━━━━━<br/>Показать роль]

    MsgRouter --> TextHandler[handle_message<br/>━━━━━━━━━<br/>1. get_context<br/>2. LLM request<br/>3. save_context]

    StartHandler & HelpHandler & RoleHandler --> Reply[message.answer]
    ClearHandler --> ClearCtx[Очистка контекста]
    ClearCtx --> Reply

    TextHandler --> LLMReply[LLM Response]
    LLMReply --> Reply

    Reply --> User[👤 Пользователь]

    style TG fill:#2d3748,stroke:#4299e1,stroke-width:2px,color:#fff
    style DP fill:#2d3748,stroke:#805ad5,stroke-width:2px,color:#fff
    style CmdRouter fill:#2d3748,stroke:#48bb78,stroke-width:2px,color:#fff
    style MsgRouter fill:#2d3748,stroke:#ed8936,stroke-width:2px,color:#fff
    style User fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#fff
```

---

## 8. 🧪 Тестовая архитектура

### Покрытие тестами

```mermaid
graph TB
    subgraph Tests["🧪 Tests Suite (58 тестов)"]
        direction TB

        subgraph Unit["Unit Tests (47 тестов)"]
            TCMD[test_commands.py<br/>━━━━━━━━━<br/>10 тестов<br/>4 команды]
            TCTX[test_context.py<br/>━━━━━━━━━<br/>13 тестов<br/>parametrized]
            TLLM[test_llm.py<br/>━━━━━━━━━<br/>9 тестов<br/>mocked OpenAI]
            TPRM[test_prompts.py<br/>━━━━━━━━━<br/>7 тестов<br/>промпты]
            TCFG[test_config.py<br/>━━━━━━━━━<br/>8 тестов<br/>валидация]
        end

        subgraph Integration["Integration Tests (11 тестов)"]
            THDL[test_handlers.py<br/>━━━━━━━━━<br/>11 тестов<br/>full flow]
        end
    end

    subgraph Code["📦 Production Code"]
        CMD[commands.py]
        MSG[messages.py]
        CTX[context.py]
        LLM[llm.py]
        PROM[prompts.py]
        CFG[config.py]
    end

    TCMD -.tests.-> CMD
    TCTX -.tests.-> CTX
    TLLM -.tests.-> LLM
    TPRM -.tests.-> PROM
    TCFG -.tests.-> CFG
    THDL -.tests.-> CMD
    THDL -.tests.-> MSG

    subgraph Coverage["📊 Coverage: 85%+"]
        COV[pytest-cov<br/>━━━━━━━━━<br/>HTML Report<br/>htmlcov/index.html]
    end

    Tests -.coverage.-> Code
    Code -.report.-> Coverage

    style Tests fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#fff
    style Unit fill:#2d3748,stroke:#68d391,stroke-width:2px,color:#fff
    style Integration fill:#2d3748,stroke:#9ae6b4,stroke-width:2px,color:#fff
    style Code fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#fff
    style Coverage fill:#1a202c,stroke:#805ad5,stroke-width:3px,color:#fff
```

---

## 9. 🔐 Конфигурация и секреты

### Environment Variables Flow

```mermaid
flowchart TD
    ENV[.env файл<br/>━━━━━━━━━<br/>TELEGRAM_TOKEN<br/>OPENAI_API_KEY<br/>OPENAI_BASE_URL<br/>...]

    DOTENV[python-dotenv<br/>━━━━━━━━━<br/>load_dotenv]

    GETENV[os.getenv<br/>━━━━━━━━━<br/>читает переменные]

    VALIDATE{Валидация<br/>━━━━━━━━━<br/>tokens exist?}

    CONFIG[Config dataclass<br/>━━━━━━━━━<br/>telegram_token ✓<br/>openai_api_key ✓<br/>defaults applied]

    ERROR[ValueError<br/>━━━━━━━━━<br/>Missing token!<br/>Exit]

    BOT[Bot Application<br/>━━━━━━━━━<br/>config используется<br/>во всех модулях]

    ENV --> DOTENV
    DOTENV --> GETENV
    GETENV --> VALIDATE

    VALIDATE -->|❌ Missing| ERROR
    VALIDATE -->|✅ Valid| CONFIG

    CONFIG --> BOT
    ERROR --> STOP([⛔ Остановка])

    subgraph Security["🔒 Безопасность"]
        GIT[.gitignore<br/>━━━━━━━━━<br/>.env исключён]
        EX[.env.example<br/>━━━━━━━━━<br/>шаблон для команды]
    end

    ENV -.excluded.-> GIT
    EX -.template.-> ENV

    style ENV fill:#2d3748,stroke:#f6ad55,stroke-width:2px,color:#fff
    style CONFIG fill:#2d3748,stroke:#48bb78,stroke-width:2px,color:#fff
    style ERROR fill:#2d3748,stroke:#fc8181,stroke-width:2px,color:#fff
    style BOT fill:#2d3748,stroke:#4299e1,stroke-width:2px,color:#fff
    style Security fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#fff
    style STOP fill:#1a202c,stroke:#fc8181,stroke-width:3px,color:#fff
```

---

## 10. 🚀 Deployment View

### Текущая архитектура развёртывания

```mermaid
graph TB
    subgraph Local["💻 Local Machine"]
        direction TB

        subgraph Runtime["Python Runtime"]
            VENV[.venv<br/>━━━━━━━━━<br/>uv managed<br/>Python 3.11+]

            subgraph Process["Bot Process"]
                BOT[bot.py<br/>━━━━━━━━━<br/>aiogram Dispatcher<br/>Long Polling]

                MEM[In-Memory Storage<br/>━━━━━━━━━<br/>user_contexts dict<br/>⚠️ volatile]
            end
        end

        subgraph Files["File System"]
            ENV[.env<br/>secrets]
            LOG[bot.log<br/>logs]
            CODE[source code]
        end
    end

    subgraph External["☁️ External Services"]
        TG_API[Telegram Bot API<br/>━━━━━━━━━<br/>api.telegram.org<br/>Long Polling]

        AI_API[OpenAI/OpenRouter<br/>━━━━━━━━━<br/>openrouter.ai<br/>Chat Completions]
    end

    ENV -.loads.-> BOT
    CODE -.runs.-> BOT
    BOT -.writes.-> LOG
    BOT <-.polling.-> TG_API
    BOT <-.API calls.-> AI_API

    BOT <-.reads/writes.-> MEM

    style Local fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#fff
    style Runtime fill:#2d3748,stroke:#48bb78,stroke-width:2px,color:#fff
    style Process fill:#2d3748,stroke:#68d391,stroke-width:2px,color:#fff
    style Files fill:#2d3748,stroke:#9f7aea,stroke-width:2px,color:#fff
    style External fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#fff
    style MEM fill:#2d3748,stroke:#fc8181,stroke-width:2px,color:#fff

    note1[⚠️ Ограничения:<br/>- In-memory storage<br/>- Single process<br/>- No persistence<br/>- Manual restart]

    style note1 fill:#2d3748,stroke:#f6ad55,stroke-width:2px,color:#fff
```

---

## 11. ⚙️ Quality Checks Pipeline

### make quality workflow

```mermaid
flowchart LR
    START([make quality]) --> FORMAT[🎨 Format<br/>━━━━━━━━━<br/>ruff format .]

    FORMAT --> FCHECK{Changes?}
    FCHECK -->|Yes| FAPPLY[Применить<br/>автоформат]
    FCHECK -->|No| LINT
    FAPPLY --> LINT

    LINT[🔍 Lint<br/>━━━━━━━━━<br/>ruff check .]

    LINT --> LCHECK{Errors?}
    LCHECK -->|Yes| LFAIL[❌ FAIL<br/>━━━━━━━━━<br/>Fix code style]
    LCHECK -->|No| TYPE

    TYPE[🔎 Type Check<br/>━━━━━━━━━<br/>mypy bot.py ...]

    TYPE --> TCHECK{Errors?}
    TCHECK -->|Yes| TFAIL[❌ FAIL<br/>━━━━━━━━━<br/>Add type hints]
    TCHECK -->|No| TEST

    TEST[🧪 Tests<br/>━━━━━━━━━<br/>pytest tests/ -v]

    TEST --> TSCHECK{All pass?}
    TSCHECK -->|No| TSFAIL[❌ FAIL<br/>━━━━━━━━━<br/>Fix tests]
    TSCHECK -->|Yes| SUCCESS

    SUCCESS([✅ All checks passed!<br/>━━━━━━━━━<br/>Ready to commit])

    LFAIL --> STOP([⛔ Fix and retry])
    TFAIL --> STOP
    TSFAIL --> STOP

    style START fill:#1a202c,stroke:#805ad5,stroke-width:3px,color:#fff
    style FORMAT fill:#2d3748,stroke:#9f7aea,stroke-width:2px,color:#fff
    style LINT fill:#2d3748,stroke:#4299e1,stroke-width:2px,color:#fff
    style TYPE fill:#2d3748,stroke:#ed8936,stroke-width:2px,color:#fff
    style TEST fill:#2d3748,stroke:#48bb78,stroke-width:2px,color:#fff
    style SUCCESS fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#fff
    style STOP fill:#1a202c,stroke:#fc8181,stroke-width:3px,color:#fff
```

---

## 12. 📈 User Journey

### Типичный сценарий использования

```mermaid
journey
    title Путь пользователя через бота
    section Первый запуск
      Найти бота в Telegram: 3: User
      Отправить /start: 5: User
      Получить приветствие: 5: User, Bot
      Прочитать /help: 4: User, Bot
    section Диалог
      Задать вопрос: 5: User
      Увидеть "typing...": 3: User, Bot
      Получить ответ: 5: User, Bot
      Продолжить диалог: 5: User, Bot
      Бот помнит контекст: 5: User, Bot
    section Управление
      История стала длинной: 3: User
      Использовать /clear: 4: User
      История очищена: 5: User, Bot
      Новый диалог: 5: User, Bot
    section Узнать о боте
      Использовать /role: 4: User
      Увидеть специализацию: 5: User, Bot
```

---

## 13. 🔄 Error Handling Flow

### Обработка ошибок LLM API

```mermaid
flowchart TD
    START[LLM Request] --> TRY{Try-Catch}

    TRY -->|Success| RESP[Response]
    RESP --> EMPTY{Empty?}
    EMPTY -->|Yes| EMSG[🤔 Пустой ответ]
    EMPTY -->|No| CLEAN[Очистка markdown]
    CLEAN --> RETURN[Return response]

    TRY -->|RateLimitError| RATE[⚠️ Слишком много<br/>запросов]
    TRY -->|APITimeoutError| TIME[⏱️ Превышено<br/>время ожидания]
    TRY -->|APIConnectionError| CONN[❌ Не удалось<br/>подключиться]
    TRY -->|APIStatusError 404| NOTF[❌ Модель<br/>не найдена]
    TRY -->|APIStatusError Other| STAT[❌ Ошибка сервиса<br/>LLM]
    TRY -->|Exception| UNK[❌ Непредвиденная<br/>ошибка]

    EMSG --> LOG[logger.warning]
    RATE --> LOG
    TIME --> LOG
    CONN --> LOG
    NOTF --> LOG
    STAT --> LOG
    UNK --> LOG2[logger.error]

    LOG --> USER[Понятное сообщение<br/>пользователю]
    LOG2 --> USER
    RETURN --> USER

    USER --> END([Бот не падает])

    style START fill:#2d3748,stroke:#4299e1,stroke-width:2px,color:#fff
    style RETURN fill:#2d3748,stroke:#48bb78,stroke-width:2px,color:#fff
    style RATE fill:#2d3748,stroke:#f6ad55,stroke-width:2px,color:#fff
    style TIME fill:#2d3748,stroke:#f6ad55,stroke-width:2px,color:#fff
    style CONN fill:#2d3748,stroke:#fc8181,stroke-width:2px,color:#fff
    style NOTF fill:#2d3748,stroke:#fc8181,stroke-width:2px,color:#fff
    style STAT fill:#2d3748,stroke:#fc8181,stroke-width:2px,color:#fff
    style UNK fill:#2d3748,stroke:#fc8181,stroke-width:2px,color:#fff
    style END fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#fff
```

---

## Итого

Этот гайд покрывает проект с **13 различных перспектив**:

1. ✅ Системная архитектура (layers)
2. ✅ Поток обработки сообщений (sequence)
3. ✅ Структура проекта (tree + dependencies)
4. ✅ Жизненный цикл контекста (state machine)
5. ✅ Модель данных (class diagram)
6. ✅ Developer workflow (flowchart + TDD)
7. ✅ Маршрутизация команд/сообщений
8. ✅ Тестовая архитектура
9. ✅ Конфигурация и секреты
10. ✅ Deployment view
11. ✅ Quality checks pipeline
12. ✅ User journey
13. ✅ Error handling flow

**Все диаграммы используют контрастные цвета для читаемости в dark theme.**

---

## Как просматривать

- **VS Code/Cursor:** Установите "Markdown Preview Mermaid Support" → `Ctrl+Shift+V`
- **GitHub:** Диаграммы рендерятся автоматически
- **Online:** [mermaid.live](https://mermaid.live/)

---

**Версия:** 1.0
**Дата:** 2025-10-16

