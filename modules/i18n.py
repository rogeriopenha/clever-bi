import streamlit as st

IDIOMAS = {
    "pt-br": {"bandeira": "🇧🇷", "nome": "Português (BR)", "nome_nativo": "Português (Brasil)"},
    "pt-pt": {"bandeira": "🇵🇹", "nome": "Português (PT)", "nome_nativo": "Português (Portugal)"},
    "es":    {"bandeira": "🇪🇸", "nome": "Español", "nome_nativo": "Español"},
    "en-us": {"bandeira": "🇺🇸", "nome": "English (US)", "nome_nativo": "English (US)"},
    "en-gb": {"bandeira": "🇬🇧", "nome": "English (UK)", "nome_nativo": "English (UK)"},
    "de":    {"bandeira": "🇩🇪", "nome": "Deutsch", "nome_nativo": "Deutsch"},
    "fr":    {"bandeira": "🇫🇷", "nome": "Français", "nome_nativo": "Français"},
    "ru":    {"bandeira": "🇷🇺", "nome": "Русский", "nome_nativo": "Русский"},
    "zh":    {"bandeira": "🇨🇳", "nome": "中文", "nome_nativo": "中文"},
    "ja":    {"bandeira": "🇯🇵", "nome": "日本語", "nome_nativo": "日本語"},
}

IDIOMA_PADRAO = "pt-br"

def get_idioma() -> str:
    return st.session_state.get("idioma", IDIOMA_PADRAO)

def get_idioma_info() -> dict:
    idioma = get_idioma()
    return IDIOMAS.get(idioma, IDIOMAS[IDIOMA_PADRAO])

T = {
    # Geral
    "app.titulo": {
        "pt-br": "CLEVER", "pt-pt": "CLEVER", "es": "CLEVER",
        "en-us": "CLEVER", "en-gb": "CLEVER", "de": "CLEVER",
        "fr": "CLEVER", "ru": "CLEVER", "zh": "CLEVER", "ja": "CLEVER",
    },
    "app.subtitulo": {
        "pt-br": "Business Intelligence", "pt-pt": "Business Intelligence",
        "es": "Inteligencia de Negocios", "en-us": "Business Intelligence",
        "en-gb": "Business Intelligence", "de": "Business Intelligence",
        "fr": "Business Intelligence", "ru": "Бизнес-аналитика",
        "zh": "商业智能", "ja": "ビジネスインテリジェンス",
    },
    "nav.dashboards": {
        "pt-br": "📊 Dashboards", "pt-pt": "📊 Dashboards",
        "es": "📊 Paneles", "en-us": "📊 Dashboards",
        "en-gb": "📊 Dashboards", "de": "📊 Dashboards",
        "fr": "📊 Tableaux", "ru": "📊 Дашборды",
        "zh": "📊 仪表盘", "ja": "📊 ダッシュボード",
    },
    "nav.ia": {
        "pt-br": "🧠 IA", "pt-pt": "🧠 IA",
        "es": "🧠 IA", "en-us": "🧠 AI",
        "en-gb": "🧠 AI", "de": "🧠 KI",
        "fr": "🧠 IA", "ru": "🧠 ИИ",
        "zh": "🧠 人工智能", "ja": "🧠 AI",
    },
    "nav.fontes": {
        "pt-br": "🔌 Fontes de Dados", "pt-pt": "🔌 Fontes de Dados",
        "es": "🔌 Fuentes de Datos", "en-us": "🔌 Data Sources",
        "en-gb": "🔌 Data Sources", "de": "🔌 Datenquellen",
        "fr": "🔌 Sources de Données", "ru": "🔌 Источники Данных",
        "zh": "🔌 数据源", "ja": "🔌 データソース",
    },
    "nav.config": {
        "pt-br": "⚙️ Configurações", "pt-pt": "⚙️ Configurações",
        "es": "⚙️ Configuración", "en-us": "⚙️ Settings",
        "en-gb": "⚙️ Settings", "de": "⚙️ Einstellungen",
        "fr": "⚙️ Paramètres", "ru": "⚙️ Настройки",
        "zh": "⚙️ 设置", "ja": "⚙️ 設定",
    },
    "nav.sair": {
        "pt-br": "🚪 Sair", "pt-pt": "🚪 Sair",
        "es": "🚪 Salir", "en-us": "🚪 Logout",
        "en-gb": "🚪 Logout", "de": "🚪 Abmelden",
        "fr": "🚪 Quitter", "ru": "🚪 Выйти",
        "zh": "🚪 退出", "ja": "🚪 ログアウト",
    },
    "nav.voltar": {
        "pt-br": "← Voltar", "pt-pt": "← Voltar",
        "es": "← Volver", "en-us": "← Back",
        "en-gb": "← Back", "de": "← Zurück",
        "fr": "← Retour", "ru": "← Назад",
        "zh": "← 返回", "ja": "← 戻る",
    },
    # Login
    "login.entrar": {
        "pt-br": "Entrar", "pt-pt": "Entrar",
        "es": "Iniciar Sesión", "en-us": "Sign In",
        "en-gb": "Sign In", "de": "Anmelden",
        "fr": "Se Connecter", "ru": "Войти",
        "zh": "登录", "ja": "ログイン",
    },
    "login.email": {
        "pt-br": "E-mail", "pt-pt": "E-mail",
        "es": "Correo", "en-us": "Email",
        "en-gb": "Email", "de": "E-Mail",
        "fr": "E-mail", "ru": "Эл. почта",
        "zh": "邮箱", "ja": "メール",
    },
    "login.senha": {
        "pt-br": "Senha", "pt-pt": "Palavra-passe",
        "es": "Contraseña", "en-us": "Password",
        "en-gb": "Password", "de": "Passwort",
        "fr": "Mot de Passe", "ru": "Пароль",
        "zh": "密码", "ja": "パスワード",
    },
    "login.criar_conta": {
        "pt-br": "Criar nova conta", "pt-pt": "Criar nova conta",
        "es": "Crear cuenta nueva", "en-us": "Create new account",
        "en-gb": "Create new account", "de": "Neues Konto erstellen",
        "fr": "Créer un compte", "ru": "Создать аккаунт",
        "zh": "创建新账户", "ja": "新規アカウント作成",
    },
    # Config
    "config.titulo": {
        "pt-br": "⚙️ Configurações", "pt-pt": "⚙️ Configurações",
        "es": "⚙️ Configuración", "en-us": "⚙️ Settings",
        "en-gb": "⚙️ Settings", "de": "⚙️ Einstellungen",
        "fr": "⚙️ Paramètres", "ru": "⚙️ Настройки",
        "zh": "⚙️ 设置", "ja": "⚙️ 設定",
    },
    "config.subtitulo": {
        "pt-br": "Configurações do sistema", "pt-pt": "Configurações do sistema",
        "es": "Configuración del sistema", "en-us": "System settings",
        "en-gb": "System settings", "de": "Systemeinstellungen",
        "fr": "Paramètres système", "ru": "Настройки системы",
        "zh": "系统设置", "ja": "システム設定",
    },
    "config.usuario": {
        "pt-br": "Usuário", "pt-pt": "Utilizador",
        "es": "Usuario", "en-us": "User",
        "en-gb": "User", "de": "Benutzer",
        "fr": "Utilisateur", "ru": "Пользователь",
        "zh": "用户", "ja": "ユーザー",
    },
    "config.funcao": {
        "pt-br": "Função", "pt-pt": "Função",
        "es": "Rol", "en-us": "Role",
        "en-gb": "Role", "de": "Rolle",
        "fr": "Rôle", "ru": "Роль",
        "zh": "角色", "ja": "役割",
    },
    "config.idioma": {
        "pt-br": "🌐 Idioma", "pt-pt": "🌐 Idioma",
        "es": "🌐 Idioma", "en-us": "🌐 Language",
        "en-gb": "🌐 Language", "de": "🌐 Sprache",
        "fr": "🌐 Langue", "ru": "🌐 Язык",
        "zh": "🌐 语言", "ja": "🌐 言語",
    },
    # Tema
    "tema.titulo": {
        "pt-br": "🎨 Tema", "pt-pt": "🎨 Tema",
        "es": "🎨 Tema", "en-us": "🎨 Theme",
        "en-gb": "🎨 Theme", "de": "🎨 Design",
        "fr": "🎨 Thème", "ru": "🎨 Тема",
        "zh": "🎨 主题", "ja": "🎨 テーマ",
    },
    "tema.selecione": {
        "pt-br": "Selecione o tema", "pt-pt": "Selecione o tema",
        "es": "Seleccione el tema", "en-us": "Select theme",
        "en-gb": "Select theme", "de": "Design auswählen",
        "fr": "Choisir le thème", "ru": "Выберите тему",
        "zh": "选择主题", "ja": "テーマを選択",
    },
    "tema.cores_atuais": {
        "pt-br": "Cores do tema atual", "pt-pt": "Cores do tema atual",
        "es": "Colores del tema actual", "en-us": "Current theme colors",
        "en-gb": "Current theme colours", "de": "Aktuelle Designfarben",
        "fr": "Couleurs du thème actuel", "ru": "Цвета текущей темы",
        "zh": "当前主题颜色", "ja": "現在のテーマカラー",
    },
    "tema.criar_editar": {
        "pt-br": "✏️ Criar / Editar tema personalizado",
        "pt-pt": "✏️ Criar / Editar tema personalizado",
        "es": "✏️ Crear / Editar tema personalizado",
        "en-us": "✏️ Create / Edit custom theme",
        "en-gb": "✏️ Create / Edit custom theme",
        "de": "✏️ Benutzerdefiniertes Design erstellen/bearbeiten",
        "fr": "✏️ Créer / Modifier un thème personnalisé",
        "ru": "✏️ Создать / Редактировать свою тему",
        "zh": "✏️ 创建/编辑自定义主题",
        "ja": "✏️ カスタムテーマを作成/編集",
    },
    "tema.salvar": {
        "pt-br": "💾 Salvar tema personalizado",
        "pt-pt": "💾 Salvar tema personalizado",
        "es": "💾 Guardar tema personalizado",
        "en-us": "💾 Save custom theme",
        "en-gb": "💾 Save custom theme",
        "de": "💾 Benutzerdefiniertes Design speichern",
        "fr": "💾 Enregistrer le thème personnalisé",
        "ru": "💾 Сохранить свою тему",
        "zh": "💾 保存自定义主题",
        "ja": "💾 カスタムテーマを保存",
    },
    "tema.excluir": {
        "pt-br": "Excluir temas personalizados",
        "pt-pt": "Excluir temas personalizados",
        "es": "Eliminar temas personalizados",
        "en-us": "Delete custom themes",
        "en-gb": "Delete custom themes",
        "de": "Benutzerdefinierte Designs löschen",
        "fr": "Supprimer les thèmes personnalisés",
        "ru": "Удалить свои темы",
        "zh": "删除自定义主题",
        "ja": "カスタムテーマを削除",
    },
    # Dashboards
    "dash.titulo": {
        "pt-br": "📊 CLEVER-BI", "pt-pt": "📊 CLEVER-BI",
        "es": "📊 CLEVER-BI", "en-us": "📊 CLEVER-BI",
        "en-gb": "📊 CLEVER-BI", "de": "📊 CLEVER-BI",
        "fr": "📊 CLEVER-BI", "ru": "📊 CLEVER-BI",
        "zh": "📊 CLEVER-BI", "ja": "📊 CLEVER-BI",
    },
    "dash.subtitulo": {
        "pt-br": "Dashboards inteligentes para suas decisões",
        "pt-pt": "Dashboards inteligentes para as suas decisões",
        "es": "Paneles inteligentes para tus decisiones",
        "en-us": "Smart dashboards for your decisions",
        "en-gb": "Smart dashboards for your decisions",
        "de": "Intelligente Dashboards für Ihre Entscheidungen",
        "fr": "Tableaux de bord intelligents pour vos décisions",
        "ru": "Умные дашборды для ваших решений",
        "zh": "智能仪表盘助力您的决策",
        "ja": "意思決定のためのスマートダッシュボード",
    },
    "dash.novo": {
        "pt-br": "➕ Novo Dashboard", "pt-pt": "➕ Novo Dashboard",
        "es": "➕ Nuevo Panel", "en-us": "➕ New Dashboard",
        "en-gb": "➕ New Dashboard", "de": "➕ Neues Dashboard",
        "fr": "➕ Nouveau Tableau", "ru": "➕ Новый дашборд",
        "zh": "➕ 新仪表盘", "ja": "➕ 新規ダッシュボード",
    },
    "dash.vazio": {
        "pt-br": "Nenhum dashboard ainda. Crie o primeiro!",
        "pt-pt": "Nenhum dashboard ainda. Crie o primeiro!",
        "es": "Aún no hay paneles. ¡Crea el primero!",
        "en-us": "No dashboards yet. Create the first one!",
        "en-gb": "No dashboards yet. Create the first one!",
        "de": "Noch keine Dashboards. Erstellen Sie das erste!",
        "fr": "Aucun tableau de bord. Créez le premier !",
        "ru": "Нет дашбордов. Создайте первый!",
        "zh": "还没有仪表盘。创建第一个！",
        "ja": "ダッシュボードがありません。最初のものを作成！",
    },
    # IA
    "ia.titulo": {
        "pt-br": "🧠 IA", "pt-pt": "🧠 IA",
        "es": "🧠 IA", "en-us": "🧠 AI",
        "en-gb": "🧠 AI", "de": "🧠 KI",
        "fr": "🧠 IA", "ru": "🧠 ИИ",
        "zh": "🧠 人工智能", "ja": "🧠 AI",
    },
    "ia.subtitulo": {
        "pt-br": "Faça perguntas sobre seus dados em linguagem natural",
        "pt-pt": "Faça perguntas sobre os seus dados em linguagem natural",
        "es": "Haz preguntas sobre tus datos en lenguaje natural",
        "en-us": "Ask questions about your data in natural language",
        "en-gb": "Ask questions about your data in natural language",
        "de": "Stellen Sie Fragen zu Ihren Daten in natürlicher Sprache",
        "fr": "Posez des questions sur vos données en langage naturel",
        "ru": "Задавайте вопросы о данных на естественном языке",
        "zh": "用自然语言询问您的数据",
        "ja": "自然言語でデータについて質問する",
    },
    # Fontes
    "fontes.titulo": {
        "pt-br": "🔌 Fontes de Dados", "pt-pt": "🔌 Fontes de Dados",
        "es": "🔌 Fuentes de Datos", "en-us": "🔌 Data Sources",
        "en-gb": "🔌 Data Sources", "de": "🔌 Datenquellen",
        "fr": "🔌 Sources de Données", "ru": "🔌 Источники Данных",
        "zh": "🔌 数据源", "ja": "🔌 データソース",
    },
    # Labels dos tokens do tema
    "token.bg_primary": {
        "pt-br": "Fundo principal", "pt-pt": "Fundo principal",
        "es": "Fondo principal", "en-us": "Main background",
        "en-gb": "Main background", "de": "Hauptgrund",
        "fr": "Fond principal", "ru": "Основной фон",
        "zh": "主背景", "ja": "メイン背景",
    },
    "token.bg_secondary": {
        "pt-br": "Fundo secundário", "pt-pt": "Fundo secundário",
        "es": "Fondo secundario", "en-us": "Secondary background",
        "en-gb": "Secondary background", "de": "Sekundärgrund",
        "fr": "Fond secondaire", "ru": "Вторичный фон",
        "zh": "次要背景", "ja": "セカンダリ背景",
    },
    "token.text_primary": {
        "pt-br": "Texto principal", "pt-pt": "Texto principal",
        "es": "Texto principal", "en-us": "Primary text",
        "en-gb": "Primary text", "de": "Haupttext",
        "fr": "Texte principal", "ru": "Основной текст",
        "zh": "主文本", "ja": "メインテキスト",
    },
    "token.text_secondary": {
        "pt-br": "Texto secundário", "pt-pt": "Texto secundário",
        "es": "Texto secundario", "en-us": "Secondary text",
        "en-gb": "Secondary text", "de": "Sekundärtext",
        "fr": "Texte secondaire", "ru": "Вторичный текст",
        "zh": "次要文本", "ja": "セカンダリテキスト",
    },
    "token.accent": {
        "pt-br": "Cor de destaque", "pt-pt": "Cor de destaque",
        "es": "Color de acento", "en-us": "Accent color",
        "en-gb": "Accent colour", "de": "Akzentfarbe",
        "fr": "Couleur d'accent", "ru": "Акцентный цвет",
        "zh": "强调色", "ja": "アクセントカラー",
    },
    "token.accent_hover": {
        "pt-br": "Destaque (hover)", "pt-pt": "Destaque (hover)",
        "es": "Acento (hover)", "en-us": "Accent hover",
        "en-gb": "Accent hover", "de": "Akzent Hover",
        "fr": "Accent survol", "ru": "Акцент при наведении",
        "zh": "悬停强调色", "ja": "アクセントホバー",
    },
    "token.border": {
        "pt-br": "Bordas", "pt-pt": "Bordas",
        "es": "Bordes", "en-us": "Borders",
        "en-gb": "Borders", "de": "Rahmen",
        "fr": "Bordures", "ru": "Границы",
        "zh": "边框", "ja": "境界線",
    },
    "token.metric_label": {
        "pt-br": "Rótulo de métrica", "pt-pt": "Rótulo de métrica",
        "es": "Etiqueta de métrica", "en-us": "Metric label",
        "en-gb": "Metric label", "de": "Metrik-Beschriftung",
        "fr": "Étiquette de métrique", "ru": "Метка метрики",
        "zh": "指标标签", "ja": "メトリックラベル",
    },
    "token.metric_value": {
        "pt-br": "Valor de métrica", "pt-pt": "Valor de métrica",
        "es": "Valor de métrica", "en-us": "Metric value",
        "en-gb": "Metric value", "de": "Metrik-Wert",
        "fr": "Valeur de métrique", "ru": "Значение метрики",
        "zh": "指标值", "ja": "メトリック値",
    },
    "token.metric_delta": {
        "pt-br": "Delta de métrica", "pt-pt": "Delta de métrica",
        "es": "Delta de métrica", "en-us": "Metric delta",
        "en-gb": "Metric delta", "de": "Metrik-Delta",
        "fr": "Delta de métrique", "ru": "Дельта метрики",
        "zh": "指标变化", "ja": "メトリックデルタ",
    },
    "token.card_bg": {
        "pt-br": "Fundo do cartão", "pt-pt": "Fundo do cartão",
        "es": "Fondo de tarjeta", "en-us": "Card background",
        "en-gb": "Card background", "de": "Kartenhintergrund",
        "fr": "Fond de carte", "ru": "Фон карточки",
        "zh": "卡片背景", "ja": "カード背景",
    },
    "token.card_border": {
        "pt-br": "Borda do cartão", "pt-pt": "Borda do cartão",
        "es": "Borde de tarjeta", "en-us": "Card border",
        "en-gb": "Card border", "de": "Kartenrahmen",
        "fr": "Bordure de carte", "ru": "Граница карточки",
        "zh": "卡片边框", "ja": "カード境界線",
    },
    "token.tab_inactive_bg": {
        "pt-br": "Aba inativa fundo", "pt-pt": "Aba inativa fundo",
        "es": "Pestaña inactiva fondo", "en-us": "Inactive tab bg",
        "en-gb": "Inactive tab bg", "de": "Inaktiver Tab-Hintergrund",
        "fr": "Onglet inactif fond", "ru": "Фон неактивной вкладки",
        "zh": "非活动标签背景", "ja": "非アクティブタブ背景",
    },
    "token.tab_inactive_color": {
        "pt-br": "Aba inativa texto", "pt-pt": "Aba inativa texto",
        "es": "Pestaña inactiva texto", "en-us": "Inactive tab text",
        "en-gb": "Inactive tab text", "de": "Inaktiver Tab-Text",
        "fr": "Onglet inactif texte", "ru": "Текст неактивной вкладки",
        "zh": "非活动标签文本", "ja": "非アクティブタブテキスト",
    },
    "token.tab_active_bg": {
        "pt-br": "Aba ativa fundo", "pt-pt": "Aba ativa fundo",
        "es": "Pestaña activa fondo", "en-us": "Active tab bg",
        "en-gb": "Active tab bg", "de": "Aktiver Tab-Hintergrund",
        "fr": "Onglet actif fond", "ru": "Фон активной вкладки",
        "zh": "活动标签背景", "ja": "アクティブタブ背景",
    },
}

def t(chave: str) -> str:
    idioma = get_idioma()
    trad = T.get(chave, {})
    return trad.get(idioma, trad.get(IDIOMA_PADRAO, chave))

def token_label(token: str) -> str:
    return t(f"token.{token}")
