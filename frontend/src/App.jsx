import { useEffect, useMemo, useState } from 'react'
import './App.css'

const EMPTY_FORM = {
  paciente: '',
  telefone: '',
  email: '',
  especialidade: '',
  medico: '',
  data: '',
  horario: '',
}

const ICON_PATHS = {
  grid: <><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></>,
  plus: <><path d="M12 5v14M5 12h14" /></>,
  search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
  chevron: <path d="m9 18 6-6-6-6" />,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  pin: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>,
  mail: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></>,
  phone: <path d="M7 3H5a2 2 0 0 0-2 2c0 8.8 7.2 16 16 16a2 2 0 0 0 2-2v-2l-5-2-2 3a14 14 0 0 1-7-7l3-2-3-5Z" />,
  trash: <><path d="M4 7h16M10 11v6M14 11v6M5 7l1 14h12l1-14M9 7V4h6v3" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  heart: <><path d="M20.8 8.6c0 5.2-8.8 11.1-8.8 11.1S3.2 13.8 3.2 8.6A4.6 4.6 0 0 1 12 6.4a4.6 4.6 0 0 1 8.8 2.2Z" /><path d="M4 12h4l2-4 3.5 8 2-4H20" /></>,
  users: <><path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="10" cy="7" r="4" /><path d="M20 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8" /></>,
  arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>,
  close: <><path d="m18 6-12 12M6 6l12 12" /></>,
  stethoscope: <><path d="M6 3v5a4 4 0 0 0 8 0V3M4 3h4M12 3h4M10 12v2a4 4 0 0 0 8 0v-1" /><circle cx="18" cy="11" r="2" /><path d="M14 18a4 4 0 1 0 8 0v-2" /></>,
}

function Icon({ name, size = 20, className = '' }) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {ICON_PATHS[name]}
    </svg>
  )
}

function localDateString(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function parseAppointmentDate(value) {
  if (!value) return null
  const parts = value.includes('/') ? value.split('/').reverse() : value.split('-')
  const [year, month, day] = parts.map(Number)
  const parsed = new Date(year, month - 1, day)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function formatDate(value, options = { day: '2-digit', month: 'short', year: 'numeric' }) {
  const date = parseAppointmentDate(value)
  return date
    ? new Intl.DateTimeFormat('pt-BR', options).format(date)
    : 'Data não informada'
}

async function fetchDashboardData() {
  const [configResponse, appointmentsResponse] = await Promise.all([
    fetch('/api/config'),
    fetch('/api/appointments'),
  ])
  const [configData, appointmentsData] = await Promise.all([
    configResponse.json(),
    appointmentsResponse.json(),
  ])
  if (!configResponse.ok || !appointmentsResponse.ok) {
    throw new Error(configData.erro || appointmentsData.erro || 'Não foi possível carregar os dados.')
  }
  return { configData, appointmentsData }
}

async function fetchCurrentUser() {
  const response = await fetch('/api/auth/me')
  const data = await response.json()
  if (response.status === 401) return null
  if (!response.ok) throw new Error(data.erro || 'Não foi possível verificar sua conta.')
  return data.usuario
}

function App() {
  const [page, setPage] = useState('inicio')
  const [config, setConfig] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [user, setUser] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [authMode, setAuthMode] = useState('login')
  const [authForm, setAuthForm] = useState({ nome: '', telefone: '', email: '', senha: '' })
  const [authError, setAuthError] = useState('')
  const [authSaving, setAuthSaving] = useState(false)
  const [availability, setAvailability] = useState({ key: '', times: [] })
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [notice, setNotice] = useState(null)
  const [error, setError] = useState('')

  const [today] = useState(() => localDateString(new Date()))
  const availabilityKey = `${form.especialidade}|${form.medico}|${form.data}`
  const availableTimes = availability.key === availabilityKey ? availability.times : []
  const doctors = config?.medicos_por_especialidade?.[form.especialidade] ?? []
  const upcomingAppointments = useMemo(() => {
    return [...appointments]
      .filter((appointment) => {
        const parsed = parseAppointmentDate(appointment.data)
        return parsed && localDateString(parsed) >= today
      })
      .sort((a, b) => {
        const dateDifference = parseAppointmentDate(a.data) - parseAppointmentDate(b.data)
        return dateDifference || a.horario.localeCompare(b.horario)
      })
  }, [appointments, today])

  const filteredAppointments = useMemo(() => {
    const term = search.trim().toLocaleLowerCase('pt-BR')
    return appointments.filter((appointment) =>
      [
        appointment.paciente,
        appointment.medico,
        appointment.especialidade,
        appointment.data,
      ]
        .join(' ')
        .toLocaleLowerCase('pt-BR')
        .includes(term),
    )
  }, [appointments, search])

  async function loadData(showLoader = true) {
    if (showLoader) setLoading(true)
    setError('')
    try {
      const { configData, appointmentsData } = await fetchDashboardData()
      setConfig(configData)
      setAppointments(appointmentsData)
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível conectar ao servidor.')
    } finally {
      if (showLoader) setLoading(false)
    }
  }

  useEffect(() => {
    let active = true
    fetchCurrentUser()
      .then(async (currentUser) => {
        if (!active || !currentUser) return
        setUser(currentUser)
        const { configData, appointmentsData } = await fetchDashboardData()
        if (active) {
          setConfig(configData)
          setAppointments(appointmentsData)
        }
      })
      .catch((requestError) => {
        if (active) setError(requestError.message || 'Não foi possível conectar ao servidor.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  async function submitAuth(event) {
    event.preventDefault()
    setAuthSaving(true)
    setAuthError('')
    try {
      const response = await fetch(`/api/auth/${authMode === 'register' ? 'register' : 'login'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(authForm),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.erro || 'Não foi possível acessar sua conta.')
      setUser(data.usuario)
      setError('')
      setPage('inicio')
      await loadData(false)
    } catch (requestError) {
      setAuthError(requestError.message || 'Não foi possível acessar sua conta.')
    } finally {
      setAuthSaving(false)
    }
  }

  async function logout() {
    try {
      const response = await fetch('/api/auth/logout', { method: 'POST' })
      if (!response.ok) throw new Error('Não foi possível sair da conta.')
      setUser(null)
      setAppointments([])
      setForm(EMPTY_FORM)
      setPage('inicio')
      setAuthMode('login')
      setAuthForm({ nome: '', telefone: '', email: user?.email ?? '', senha: '' })
      setNotice(null)
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível sair da conta.')
    }
  }

  useEffect(() => {
    if (!form.medico || !form.especialidade || !form.data) {
      return
    }

    let active = true
    const requestKey = `${form.especialidade}|${form.medico}|${form.data}`
    const params = new URLSearchParams({
      especialidade: form.especialidade,
      medico: form.medico,
      data: form.data,
    })
    fetch(`/api/availability?${params}`)
      .then(async (response) => {
        const data = await response.json()
        if (!response.ok) throw new Error(data.erro || 'Não foi possível carregar os horários.')
        if (active) setAvailability({ key: requestKey, times: data.horarios })
      })
      .catch((requestError) => {
        if (active) {
          setAvailability({ key: requestKey, times: [] })
          setNotice({ type: 'error', text: requestError.message })
        }
      })
    return () => {
      active = false
    }
  }, [form.medico, form.especialidade, form.data])

  function updateForm(field, value) {
    setForm((current) => {
      const next = { ...current, [field]: value }
      if (field === 'especialidade') {
        next.medico = ''
        next.data = ''
        next.horario = ''
      } else if (field === 'medico' || field === 'data') {
        next.horario = ''
      }
      return next
    })
  }

  async function submitAppointment(event) {
    event.preventDefault()
    setSaving(true)
    setNotice(null)
    try {
      const response = await fetch('/api/appointments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          especialidade: form.especialidade,
          medico: form.medico,
          data: form.data,
          horario: form.horario,
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.erro || 'Não foi possível agendar a consulta.')
      await loadData(false)
      setForm(EMPTY_FORM)
      setPage('agendamentos')
      setNotice({
        type: data.email_enviado ? 'success' : 'warning',
        text: data.email_enviado
          ? 'Consulta agendada! A confirmação foi enviada por e-mail.'
          : `Consulta agendada, mas o e-mail não foi enviado${data.aviso ? `: ${data.aviso}` : '.'}`,
      })
    } catch (requestError) {
      setNotice({ type: 'error', text: requestError.message || 'Falha ao agendar a consulta.' })
    } finally {
      setSaving(false)
    }
  }

  async function cancelAppointment(appointment) {
    if (!window.confirm(`Deseja cancelar a consulta de ${appointment.paciente}?`)) return
    setNotice(null)
    try {
      const response = await fetch(`/api/appointments/${encodeURIComponent(appointment.id)}`, {
        method: 'DELETE',
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.erro || 'Não foi possível cancelar a consulta.')
      setAppointments((current) => current.filter((item) => item.id !== appointment.id))
      setNotice({ type: 'success', text: 'Agendamento cancelado com sucesso.' })
    } catch (requestError) {
      setNotice({ type: 'error', text: requestError.message || 'Falha ao cancelar o agendamento.' })
    }
  }

  function openBooking() {
    setNotice(null)
    setPage('agendar')
  }

  if (!loading && !user) {
    return (
      <main className="auth-screen">
        <section className="auth-card card">
          <div className="auth-brand">
            <span className="brand-mark"><Icon name="heart" size={23} /></span>
            <span className="brand-name">adriana<span>soares</span></span>
          </div>
          <p className="eyebrow">ÁREA DO PACIENTE</p>
          <h1>{authMode === 'login' ? 'Acesse sua conta' : 'Crie sua conta'}</h1>
          <p className="auth-subtitle">
            {authMode === 'login'
              ? 'Entre para consultar e gerenciar seus agendamentos.'
              : 'Cadastre-se para agendar e acompanhar suas consultas.'}
          </p>
          <div className="auth-switch" role="group" aria-label="Tipo de acesso">
            <button
              type="button"
              className={authMode === 'login' ? 'active' : ''}
              onClick={() => { setAuthMode('login'); setAuthError('') }}
            >
              Entrar
            </button>
            <button
              type="button"
              className={authMode === 'register' ? 'active' : ''}
              onClick={() => { setAuthMode('register'); setAuthError('') }}
            >
              Criar conta
            </button>
          </div>
          <form className="auth-form" onSubmit={submitAuth}>
            {error && <p className="auth-error" role="alert">{error} Confira se a API está em execução.</p>}
            {authMode === 'register' && (
              <>
                <label className="field">
                  <span>Nome completo</span>
                  <input
                    autoComplete="name"
                    maxLength={120}
                    required
                    value={authForm.nome}
                    onChange={(event) => setAuthForm({ ...authForm, nome: event.target.value })}
                  />
                </label>
                <label className="field">
                  <span>Telefone</span>
                  <input
                    autoComplete="tel"
                    maxLength={30}
                    required
                    value={authForm.telefone}
                    onChange={(event) => setAuthForm({ ...authForm, telefone: event.target.value })}
                  />
                </label>
              </>
            )}
            <label className="field">
              <span>E-mail</span>
              <input
                autoComplete="username"
                maxLength={254}
                required
                type="email"
                value={authForm.email}
                onChange={(event) => setAuthForm({ ...authForm, email: event.target.value })}
              />
            </label>
            <label className="field">
              <span>Senha</span>
              <input
                autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                maxLength={128}
                minLength={8}
                required
                type="password"
                value={authForm.senha}
                onChange={(event) => setAuthForm({ ...authForm, senha: event.target.value })}
              />
            </label>
            {authError && <p className="auth-error" role="alert">{authError}</p>}
            <button className="button button-primary auth-submit" disabled={authSaving} type="submit">
              {authSaving ? 'Aguarde...' : authMode === 'login' ? 'Entrar' : 'Criar conta'}
              <Icon name="arrow" size={17} />
            </button>
          </form>
        </section>
      </main>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={(event) => { event.preventDefault(); setPage('inicio') }}>
          <span className="brand-mark"><Icon name="heart" size={23} /></span>
          <span className="brand-name">adriana<span>soares</span></span>
        </a>
        <p className="sidebar-label">MENU PRINCIPAL</p>
        <nav className="navigation" aria-label="Navegação principal">
          <button className={`nav-link ${page === 'inicio' ? 'active' : ''}`} onClick={() => setPage('inicio')}>
            <Icon name="grid" /><span>Visão geral</span>
          </button>
          <button className={`nav-link ${page === 'agendamentos' ? 'active' : ''}`} onClick={() => setPage('agendamentos')}>
            <Icon name="calendar" /><span>Meus agendamentos</span>
            <span className="nav-count">{appointments.length}</span>
          </button>
          <button className={`nav-link ${page === 'agendar' ? 'active' : ''}`} onClick={openBooking}>
            <Icon name="plus" /><span>Agendar consulta</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <span className="help-icon"><Icon name="phone" size={18} /></span>
            <p>Precisa de ajuda?</p>
            <span>Fale com nossa equipe</span>
            <a href="tel:+551124001234">(11) 2400-1234</a>
          </div>
          <div className="sidebar-location"><Icon name="pin" size={16} /><span>Guarulhos, SP</span></div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="mobile-brand"><span className="brand-mark"><Icon name="heart" size={20} /></span> Adriana Soares</div>
          <div className="breadcrumb"><span>Hospital</span><Icon name="chevron" size={15} /><strong>{page === 'inicio' ? 'Visão geral' : page === 'agendar' ? 'Agendar consulta' : 'Agendamentos'}</strong></div>
          <div className="topbar-profile">
            <span className="online-dot" />
            <span className="profile-copy"><strong>{user?.nome}</strong><small>Paciente</small></span>
            <span className="avatar">{user?.nome?.slice(0, 2).toUpperCase() ?? 'P'}</span>
            <button className="logout-button" onClick={logout} type="button">Sair</button>
          </div>
        </header>

        <div className="page-content">
          {error && (
            <div className="notice error-notice" role="alert">
              <span>{error} Confira se a API está em execução.</span>
              <button className="text-button" onClick={() => loadData()} type="button">Tentar novamente</button>
            </div>
          )}
          {notice && (
            <div className={`notice ${notice.type}-notice`} role="status">
              <span>{notice.text}</span>
              <button className="notice-close" aria-label="Fechar aviso" onClick={() => setNotice(null)}><Icon name="close" size={17} /></button>
            </div>
          )}

          {loading ? (
            <div className="loading-state"><span className="spinner" /> Carregando informações...</div>
          ) : page === 'agendar' ? (
            <section className="booking-page">
              <div className="page-heading">
                <div>
                  <p className="eyebrow">CUIDADO COM VOCÊ</p>
                  <h1>Agende sua consulta</h1>
                  <p className="page-subtitle">Escolha a especialidade, o profissional e o melhor horário.</p>
                </div>
                <span className="heading-icon"><Icon name="calendar" size={24} /></span>
              </div>
              <form className="booking-layout" onSubmit={submitAppointment}>
                <div className="booking-form card">
                  <div className="form-section-title"><span className="step-number">01</span><div><h2>Dados do paciente</h2><p>Como podemos entrar em contato?</p></div></div>
                  <div className="account-summary">
                    <strong>{user?.nome}</strong>
                    <span>{user?.telefone} · {user?.email}</span>
                  </div>

                  <div className="form-divider" />
                  <div className="form-section-title"><span className="step-number">02</span><div><h2>Detalhes da consulta</h2><p>Selecione o atendimento ideal para você.</p></div></div>
                  <div className="form-grid">
                    <label className="field">
                      <span>Especialidade</span>
                      <select required value={form.especialidade} onChange={(event) => updateForm('especialidade', event.target.value)}>
                        <option value="">Selecione uma especialidade</option>
                        {(config?.medicos_por_especialidade ? Object.keys(config.medicos_por_especialidade) : []).map((specialty) => <option key={specialty} value={specialty}>{specialty}</option>)}
                      </select>
                    </label>
                    <label className="field">
                      <span>Profissional</span>
                      <select required disabled={!doctors.length} value={form.medico} onChange={(event) => updateForm('medico', event.target.value)}>
                        <option value="">{doctors.length ? 'Selecione um profissional' : 'Escolha uma especialidade primeiro'}</option>
                        {doctors.map((doctor) => <option key={doctor} value={doctor}>{doctor}</option>)}
                      </select>
                    </label>
                    <label className="field">
                      <span>Data da consulta</span>
                      <input type="date" min={today} required disabled={!form.medico} value={form.data} onChange={(event) => updateForm('data', event.target.value)} />
                    </label>
                  </div>

                  <div className="time-picker">
                    <div className="time-picker-heading"><span>Horários disponíveis</span>{form.data && <small>{formatDate(form.data)}</small>}</div>
                    {!form.data ? (
                      <p className="field-hint">Selecione o profissional e a data para ver os horários.</p>
                    ) : availableTimes.length ? (
                      <div className="time-options">
                        {availableTimes.map((time) => (
                          <button key={time} type="button" className={`time-option ${form.horario === time ? 'selected' : ''}`} onClick={() => updateForm('horario', time)}>
                            <Icon name="clock" size={16} /> {time}
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="field-hint">Não há horários disponíveis nesta data. Escolha outra.</p>
                    )}
                  </div>

                  <div className="form-actions">
                    <button className="button button-secondary" type="button" onClick={() => setPage('inicio')}>Voltar</button>
                    <button className="button button-primary" type="submit" disabled={saving || !form.horario}>
                      {saving ? 'Agendando...' : 'Confirmar agendamento'} <Icon name="arrow" size={17} />
                    </button>
                  </div>
                </div>

                <aside className="booking-aside">
                  <div className="booking-info-card">
                    <span className="info-card-icon"><Icon name="heart" size={22} /></span>
                    <h3>Seu bem-estar em primeiro lugar</h3>
                    <p>Agende com praticidade e receba a confirmação da consulta no seu e-mail.</p>
                    <div className="info-divider" />
                    <div className="location-line"><Icon name="pin" size={17} /><span>{config?.local ?? 'Hospital Adriana Soares'}</span></div>
                  </div>
                  <div className="secure-note"><Icon name="check" size={16} /> Seus dados são usados para gerenciar o agendamento.</div>
                </aside>
              </form>
            </section>
          ) : page === 'agendamentos' ? (
            <section>
              <div className="page-heading">
                <div><p className="eyebrow">ORGANIZE SEU CUIDADO</p><h1>Meus agendamentos</h1><p className="page-subtitle">Acompanhe e gerencie suas consultas.</p></div>
                <button className="button button-primary" onClick={openBooking}><Icon name="plus" size={17} /> Nova consulta</button>
              </div>
              <div className="appointments-card card">
                <div className="table-toolbar">
                  <div><h2>Suas consultas</h2><p>{appointments.length} {appointments.length === 1 ? 'agendamento' : 'agendamentos'}</p></div>
                  <label className="search-field"><Icon name="search" size={18} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar consulta..." aria-label="Buscar agendamento" /></label>
                </div>
                {filteredAppointments.length ? (
                  <div className="table-scroll">
                    <table>
                      <thead><tr><th>Paciente</th><th>Especialidade / médico</th><th>Data e horário</th><th>Local</th><th><span className="sr-only">Ações</span></th></tr></thead>
                      <tbody>
                        {filteredAppointments.map((appointment) => {
                          const upcoming = (parseAppointmentDate(appointment.data) ?? new Date(0)) >= parseAppointmentDate(today)
                          return (
                            <tr key={appointment.id}>
                              <td><div className="patient-cell"><span className="patient-avatar">{appointment.paciente?.slice(0, 1).toUpperCase() ?? 'P'}</span><div><strong>{appointment.paciente}</strong><small>{appointment.telefone || appointment.email || 'Paciente'}</small></div></div></td>
                              <td><strong className="table-primary">{appointment.especialidade}</strong><small className="table-secondary">{appointment.medico}</small></td>
                              <td><strong className="table-primary">{formatDate(appointment.data)}</strong><small className="table-secondary">{appointment.horario}</small></td>
                              <td><span className="location-cell"><Icon name="pin" size={15} /> {appointment.local}</span></td>
                              <td><button className="icon-button danger-button" title="Cancelar consulta" aria-label={`Cancelar consulta de ${appointment.paciente}`} disabled={!upcoming} onClick={() => cancelAppointment(appointment)}><Icon name="trash" size={18} /></button></td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="empty-state"><span className="empty-icon"><Icon name={search ? 'search' : 'calendar'} size={25} /></span><h3>{search ? 'Nenhum resultado encontrado' : 'Você ainda não tem consultas'}</h3><p>{search ? 'Tente buscar por outro nome, médico ou especialidade.' : 'Agende sua primeira consulta para cuidar da sua saúde.'}</p>{!search && <button className="button button-primary" onClick={openBooking}><Icon name="plus" size={17} /> Agendar consulta</button>}</div>
                )}
              </div>
            </section>
          ) : (
            <section className="dashboard-page">
              <div className="page-heading dashboard-heading">
                <div><p className="eyebrow">HOSPITAL ADRIANA SOARES</p><h1>Olá, seja bem-vindo(a) <span className="wave">✦</span></h1><p className="page-subtitle">Seu cuidado começa com um próximo passo.</p></div>
                <button className="button button-primary" onClick={openBooking}><Icon name="plus" size={17} /> Agendar consulta</button>
              </div>

              <div className="welcome-banner">
                <div className="welcome-copy">
                  <span className="welcome-kicker"><span className="welcome-dot" /> CUIDADO QUE ACOLHE</span>
                  <h2>Sua saúde merece<br />um cuidado especial.</h2>
                  <p>Encontre o profissional certo e agende seu atendimento com praticidade.</p>
                  <button className="banner-button" onClick={openBooking}>Encontrar um profissional <Icon name="arrow" size={17} /></button>
                </div>
                <div className="banner-art" aria-hidden="true">
                  <span className="art-ring ring-one" /><span className="art-ring ring-two" />
                  <span className="art-cross"><i /><b /></span>
                  <span className="art-spark spark-one">✦</span><span className="art-spark spark-two">✦</span>
                  <span className="art-leaf leaf-one" /><span className="art-leaf leaf-two" />
                </div>
              </div>

              <div className="stats-grid">
                <article className="stat-card card"><span className="stat-icon mint"><Icon name="calendar" size={20} /></span><div><p>Total de consultas</p><strong>{appointments.length}</strong><small>consultas cadastradas</small></div></article>
                <article className="stat-card card"><span className="stat-icon peach"><Icon name="clock" size={20} /></span><div><p>Próximas consultas</p><strong>{upcomingAppointments.length}</strong><small>agendamentos futuros</small></div></article>
                <article className="stat-card card"><span className="stat-icon lavender"><Icon name="stethoscope" size={20} /></span><div><p>Especialidades</p><strong>{Object.keys(config?.medicos_por_especialidade ?? {}).length}</strong><small>áreas de atendimento</small></div></article>
              </div>

              <div className="dashboard-bottom">
                <section className="upcoming-card card">
                  <div className="section-heading"><div><h2>Próximas consultas</h2><p>Seus atendimentos agendados</p></div><button className="link-button" onClick={() => setPage('agendamentos')}>Ver todos <Icon name="arrow" size={16} /></button></div>
                  {upcomingAppointments.length ? (
                    <div className="upcoming-list">
                      {upcomingAppointments.slice(0, 3).map((appointment) => (
                        <article className="upcoming-item" key={appointment.id}>
                          <span className="appointment-date"><strong>{formatDate(appointment.data, { day: '2-digit' })}</strong><small>{formatDate(appointment.data, { month: 'short' }).replace('.', '')}</small></span>
                          <span className="appointment-color-bar" />
                          <div className="upcoming-details"><strong>{appointment.especialidade}</strong><span>{appointment.medico}</span></div>
                          <div className="upcoming-time"><Icon name="clock" size={15} /> {appointment.horario}</div>
                          <span className="status-pill">Confirmada</span>
                        </article>
                      ))}
                    </div>
                  ) : (
                    <div className="upcoming-empty"><span className="empty-icon small"><Icon name="calendar" size={19} /></span><div><strong>Nenhuma consulta próxima</strong><p>Quando você agendar, seus atendimentos aparecerão aqui.</p></div><button className="link-button" onClick={openBooking}>Agendar <Icon name="arrow" size={15} /></button></div>
                  )}
                </section>

                <aside className="care-card">
                  <span className="care-icon"><Icon name="users" size={21} /></span>
                  <p className="eyebrow">ESTAMOS AQUI POR VOCÊ</p>
                  <h3>Conte com nossa equipe</h3>
                  <p>Em caso de dúvidas, estamos prontos para ajudar.</p>
                  <a href="tel:+551124001234"><Icon name="phone" size={16} /> (11) 2400-1234</a>
                  <a href="mailto:atendimento@hospitaladriana.com.br"><Icon name="mail" size={16} /> Fale conosco</a>
                </aside>
              </div>
              <footer className="page-footer">Hospital Adriana Soares <span>•</span> Cuidar de você é a nossa prioridade.</footer>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
