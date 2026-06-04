import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare,
  Phone,
  Users,
  Instagram,
  Zap,
  BarChart3,
  Check,
  ArrowRight,
  Star,
  ShieldCheck,
  Clock,
  Sparkles,
  CheckCheck,
  Mic,
  PhoneOff,
  Volume2,
  Signal,
  Wifi,
  BatteryFull,
} from 'lucide-react'
import { useAuthStore } from '../../stores/auth.store'
import { Logo } from '../../components/ui/Logo'

const FEATURES = [
  { icon: MessageSquare, title: 'Agente WhatsApp IA', desc: 'Responde 24/7, califica leads y agenda citas automáticamente.' },
  { icon: Phone, title: 'Agente de voz IA', desc: 'Contesta y realiza llamadas en español natural.' },
  { icon: Users, title: 'CRM automático', desc: 'Cada contacto y conversación se registra solo (HubSpot).' },
  { icon: Instagram, title: 'Contenido Instagram', desc: 'Posts con imagen y texto generados por IA, listos para aprobar.' },
  { icon: Zap, title: 'Automatizaciones', desc: 'Seguimientos, recordatorios y reportes sin que muevas un dedo.' },
  { icon: BarChart3, title: 'Dashboard unificado', desc: 'Mira todo tu negocio en tiempo real, en un solo lugar.' },
]

const STEPS = [
  { n: 1, title: 'Crea tu cuenta', desc: 'Regístrate en 2 minutos y obtén 14 días gratis, sin tarjeta.' },
  { n: 2, title: 'Conecta WhatsApp', desc: 'Vincula tu WhatsApp Business y entrena al agente con tu negocio.' },
  { n: 3, title: 'Vende en automático', desc: 'Tu agente atiende, califica y agenda mientras tú te enfocas en crecer.' },
]

const STATS = [
  { value: '24/7', label: 'Atención sin descanso' },
  { value: '< 3s', label: 'Tiempo de respuesta' },
  { value: '+40%', label: 'Más leads atendidos' },
  { value: '14 días', label: 'Gratis para probar' },
]

const TESTIMONIALS = [
  {
    quote: 'Antes perdía clientes por no contestar a tiempo. Ahora el agente responde al instante y agenda solo. Recuperé la inversión el primer mes.',
    name: 'María Quispe',
    role: 'Clínica dental, Arequipa',
  },
  {
    quote: 'Lo conecté a mi WhatsApp en una tarde. Responde como si fuera yo y nunca se cansa. Mis ventas por chat subieron muchísimo.',
    name: 'Carlos Mendoza',
    role: 'Tienda de tecnología, Lima',
  },
  {
    quote: 'El agente de voz contesta las llamadas que antes se perdían. Mis clientes ni notan que es IA. Increíble para el precio.',
    name: 'Lucía Ramírez',
    role: 'Inmobiliaria, Trujillo',
  },
]

const PLANS = [
  {
    name: 'Inicial',
    price: 149,
    highlight: false,
    features: ['200 mensajes/mes', 'Agente WhatsApp IA', 'Dashboard', 'Configuración del agente'],
  },
  {
    name: 'Basic',
    price: 249,
    highlight: false,
    features: ['400 mensajes/mes', 'Agente WhatsApp IA', 'Contactos (CRM)', 'Dashboard'],
  },
  {
    name: 'Professional',
    price: 449,
    highlight: true,
    features: ['1,500 mensajes/mes', '60 llamadas de voz/mes', 'Todo lo de Basic', 'Instagram con IA', 'Citas + recordatorios', 'Reporte semanal'],
  },
  {
    name: 'Enterprise',
    price: 799,
    highlight: false,
    features: ['4,000 mensajes/mes', '150 llamadas/mes', 'Todo lo de Professional', 'Reactivación de contactos', 'Automatizaciones', 'Soporte prioritario'],
  },
]

const BADGES = [
  { icon: ShieldCheck, label: 'Datos protegidos · Ley 29733' },
  { icon: Clock, label: 'Activo en minutos' },
  { icon: Sparkles, label: 'Potenciado por IA de última generación' },
]

export function LandingPage() {
  const token = useAuthStore((s) => s.token)

  return (
    <div className="min-h-screen text-text-primary">
      {/* Nav */}
      <header className="sticky top-0 z-30 border-b border-border/60 bg-background/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <Logo size={36} showText textClassName="text-xl" />
          <nav className="flex items-center gap-4">
            <a href="#como-funciona" className="hidden text-sm text-text-secondary hover:text-text-primary sm:block">Cómo funciona</a>
            <a href="#planes" className="text-sm text-text-secondary hover:text-text-primary">Planes</a>
            {token ? (
              <Link to="/app" className="btn-primary">Ir al dashboard</Link>
            ) : (
              <>
                <Link to="/login" className="hidden text-sm text-text-secondary hover:text-text-primary sm:block">Iniciar sesión</Link>
                <Link to="/register" className="btn-primary">Empezar gratis</Link>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 pt-16 pb-12 lg:grid-cols-2 lg:pt-24">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
              <Sparkles className="h-3.5 w-3.5" /> IA para negocios peruanos 🇵🇪
            </span>
            <h1 className="mt-6 font-heading text-4xl font-bold leading-[1.1] md:text-5xl lg:text-6xl">
              Tu negocio atendiendo clientes <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">24/7 con IA</span>
            </h1>
            <p className="mt-5 max-w-xl text-lg text-text-secondary">
              WhatsApp, llamadas, Instagram y CRM — todo automatizado.
              Configúralo en minutos y deja que tu agente venda mientras tú duermes.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link to="/register" className="btn-primary px-6 py-3 text-base">
                Empezar gratis <ArrowRight className="h-4 w-4" />
              </Link>
              <a href="#planes" className="rounded-lg border border-border px-6 py-3 text-sm font-semibold hover:bg-text-primary/5">
                Ver planes
              </a>
            </div>
            <div className="mt-6 flex items-center gap-2 text-sm text-text-secondary">
              <div className="flex text-warning">
                {[0, 1, 2, 3, 4].map((i) => (
                  <Star key={i} className="h-4 w-4 fill-current" />
                ))}
              </div>
              <span>14 días gratis · sin tarjeta · cancela cuando quieras</span>
            </div>
          </motion.div>

          {/* Demo de chat animada */}
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: 24 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="flex justify-center lg:justify-end"
          >
            <PhoneDemo />
          </motion.div>
        </div>

        {/* Badges de confianza */}
        <div className="mx-auto max-w-6xl px-6 pb-8">
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3 rounded-2xl border border-border bg-card/60 px-6 py-4 backdrop-blur-sm">
            {BADGES.map((b) => (
              <div key={b.label} className="flex items-center gap-2 text-sm text-text-secondary">
                <b.icon className="h-4 w-4 text-primary" />
                {b.label}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.label} className="text-center">
              <div className="font-heading text-3xl font-bold text-primary md:text-4xl">{s.value}</div>
              <div className="mt-1 text-sm text-text-secondary">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        <h2 className="text-center font-heading text-3xl font-bold">Todo lo que tu negocio necesita</h2>
        <p className="mx-auto mt-2 max-w-xl text-center text-text-secondary">
          Una sola plataforma reemplaza al recepcionista, al community manager y al vendedor que nunca duerme.
        </p>
        <div className="mt-10 grid grid-cols-1 gap-5 md:grid-cols-3">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              whileHover={{ y: -4 }}
              className="card-base transition-shadow hover:shadow-xl hover:shadow-primary/5"
            >
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="mb-1 font-heading font-semibold">{f.title}</h3>
              <p className="text-sm text-text-secondary">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Cómo funciona */}
      <section id="como-funciona" className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-center font-heading text-3xl font-bold">Listo en 3 pasos</h2>
        <p className="mt-2 text-center text-text-secondary">Sin instalaciones complicadas. Tú te enfocas en vender.</p>
        <div className="relative mt-12 grid grid-cols-1 gap-8 md:grid-cols-3">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="relative text-center"
            >
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-secondary font-heading text-xl font-bold text-white shadow-lg shadow-primary/20">
                {s.n}
              </div>
              <h3 className="mt-5 font-heading text-lg font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-text-secondary">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Testimonios */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        <h2 className="text-center font-heading text-3xl font-bold">Negocios que ya venden con IA</h2>
        <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="card-base flex flex-col"
            >
              <div className="mb-3 flex text-warning">
                {[0, 1, 2, 3, 4].map((s) => (
                  <Star key={s} className="h-4 w-4 fill-current" />
                ))}
              </div>
              <p className="flex-1 text-sm leading-relaxed text-text-secondary">“{t.quote}”</p>
              <div className="mt-4 border-t border-border pt-3">
                <p className="text-sm font-semibold text-text-primary">{t.name}</p>
                <p className="text-xs text-text-secondary">{t.role}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="planes" className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="mb-2 text-center font-heading text-3xl font-bold">Planes simples y transparentes</h2>
        <p className="mb-10 text-center text-text-secondary">Sin permanencia. Cancela cuando quieras.</p>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {PLANS.map((plan) => (
            <div
              key={plan.name}
              className={`card-base flex flex-col ${plan.highlight ? 'border-primary shadow-xl shadow-primary/10 ring-1 ring-primary md:-translate-y-2' : ''}`}
            >
              {plan.highlight && (
                <span className="mb-2 self-start rounded-full bg-primary px-2 py-0.5 text-xs font-semibold text-white">
                  Más popular
                </span>
              )}
              <h3 className="font-heading text-xl font-bold">{plan.name}</h3>
              <div className="my-3">
                <span className="text-3xl font-bold">S/ {plan.price}</span>
                <span className="text-sm text-text-secondary">/mes</span>
              </div>
              <ul className="mb-6 flex-1 space-y-2">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-text-secondary">
                    <Check className="h-4 w-4 flex-shrink-0 text-primary" /> {f}
                  </li>
                ))}
              </ul>
              <Link
                to={`/register?plan=${plan.name.toLowerCase()}`}
                className={plan.highlight ? 'btn-primary justify-center' : 'rounded-lg border border-border px-4 py-2 text-center text-sm font-semibold hover:bg-text-primary/5'}
              >
                Elegir {plan.name}
              </Link>
            </div>
          ))}
        </div>
        <p className="mt-4 text-center text-xs text-text-secondary">Todos los planes incluyen 14 días de prueba gratis. Límites mensuales sujetos a política de uso justo.</p>
      </section>

      {/* CTA final */}
      <section className="mx-auto max-w-5xl px-6 py-16">
        <div className="relative overflow-hidden rounded-3xl border border-primary/20 bg-gradient-to-br from-primary/15 via-card to-secondary/10 px-8 py-14 text-center">
          <h2 className="font-heading text-3xl font-bold md:text-4xl">¿Listo para automatizar tu negocio?</h2>
          <p className="mx-auto mt-3 max-w-lg text-text-secondary">
            Empieza hoy y ten tu agente IA atendiendo en minutos. 14 días gratis, sin tarjeta.
          </p>
          <Link to="/register" className="btn-primary mt-7 inline-flex px-6 py-3 text-base">
            Crear mi cuenta <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      <footer className="border-t border-border py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 px-6 text-center">
          <Logo size={32} showText textClassName="text-lg" />
          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-sm text-text-secondary">
            <Link to="/privacidad" className="hover:text-text-primary">Política de Privacidad</Link>
            <span className="opacity-40">·</span>
            <Link to="/terminos" className="hover:text-text-primary">Términos y Condiciones</Link>
          </div>
          <p className="text-sm text-text-secondary">
            © {new Date().getFullYear()} AgentePro — Hecho con 💚 por Italo Eduardo Reyes Cordero · Perú 🇵🇪
          </p>
          <p className="text-xs text-text-secondary/70">
            Todos los derechos reservados. Software protegido por Derecho de Autor (D. Leg. N.º 822).
          </p>
        </div>
      </footer>
    </div>
  )
}

/* ───────────────────────────────────────────────────────────────────────────
   Demo en celular: un mockup realista de teléfono que alterna en bucle entre
   un chat de WhatsApp (el agente responde solo) y una llamada de voz con IA.
   Muestra el producto en vivo en la landing.
   ─────────────────────────────────────────────────────────────────────────── */
interface DemoMsg {
  from: 'client' | 'agent'
  text: string
}

const DEMO_MESSAGES: DemoMsg[] = [
  { from: 'client', text: '¡Hola! ¿Están abiertos hoy?' },
  { from: 'agent', text: '¡Hola! 👋 Sí, atendemos hasta las 8pm. ¿En qué te ayudo?' },
  { from: 'client', text: 'Quiero reservar una cita para mañana' },
  { from: 'agent', text: '¡Claro! Tengo 10am, 2pm o 5pm. ¿Cuál prefieres? 📅' },
  { from: 'client', text: 'A las 2pm 🙌' },
  { from: 'agent', text: '¡Listo! Te agendé mañana 2pm. Te enviaré un recordatorio. ✅' },
]

const SCENE_DURATION = { chat: 11000, call: 7000 }

function PhoneDemo() {
  const [scene, setScene] = useState<'chat' | 'call'>('chat')

  useEffect(() => {
    const t = setTimeout(
      () => setScene((s) => (s === 'chat' ? 'call' : 'chat')),
      SCENE_DURATION[scene],
    )
    return () => clearTimeout(t)
  }, [scene])

  return (
    <div className="w-full max-w-[290px]">
      {/* Marco del celular */}
      <div className="relative rounded-[2.6rem] border border-white/10 bg-neutral-900 p-2.5 shadow-2xl shadow-primary/20">
        {/* Notch / isla dinámica */}
        <div className="absolute left-1/2 top-2.5 z-20 h-5 w-24 -translate-x-1/2 rounded-b-2xl bg-neutral-900" />
        {/* Pantalla */}
        <div className="relative h-[500px] overflow-hidden rounded-[2.1rem] bg-black">
          <AnimatePresence mode="wait">
            {scene === 'chat' ? (
              <motion.div
                key="chat"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.4 }}
                className="h-full"
              >
                <ChatScene />
              </motion.div>
            ) : (
              <motion.div
                key="call"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.4 }}
                className="h-full"
              >
                <CallScene />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
      <p className="mt-3 text-center text-xs text-text-secondary">
        Demo · tu agente atiende chats y llamadas
      </p>
    </div>
  )
}

/** Barra de estado del teléfono (hora, señal, wifi, batería). */
function StatusBar({ light = false }: { light?: boolean }) {
  const c = light ? 'text-white' : 'text-white'
  return (
    <div className={`flex items-center justify-between px-5 pt-2 pb-1 text-[11px] font-medium ${c}`}>
      <span>9:41</span>
      <div className="flex items-center gap-1">
        <Signal className="h-3 w-3" />
        <Wifi className="h-3 w-3" />
        <BatteryFull className="h-3.5 w-3.5" />
      </div>
    </div>
  )
}

/** Escena 1: chat de WhatsApp con el agente respondiendo solo. */
function ChatScene() {
  const [count, setCount] = useState(1)

  useEffect(() => {
    setCount(1)
  }, [])

  useEffect(() => {
    if (count >= DEMO_MESSAGES.length) return
    const next = setTimeout(() => setCount((c) => c + 1), 1500)
    return () => clearTimeout(next)
  }, [count])

  const visible = DEMO_MESSAGES.slice(0, count)

  return (
    <div className="flex h-full flex-col bg-[#0b141a]">
      {/* Header WhatsApp */}
      <div className="bg-[#1f2c34]">
        <StatusBar />
        <div className="flex items-center gap-2.5 px-3 pb-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/15">
            <Logo size={22} />
          </div>
          <div className="flex-1">
            <p className="text-[13px] font-semibold leading-tight text-white">Tu Negocio</p>
            <p className="text-[10px] text-emerald-300">en línea · responde al instante</p>
          </div>
          <Phone className="h-4 w-4 text-white/70" />
        </div>
      </div>

      {/* Mensajes */}
      <div className="flex flex-1 flex-col gap-2 overflow-hidden p-3">
        <AnimatePresence initial={false}>
          {visible.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.25 }}
              className={m.from === 'agent' ? 'flex justify-end' : 'flex justify-start'}
            >
              <div
                className={
                  m.from === 'agent'
                    ? 'max-w-[82%] rounded-2xl rounded-tr-sm bg-[#005c4b] px-3 py-2 text-[13px] leading-snug text-white'
                    : 'max-w-[82%] rounded-2xl rounded-tl-sm bg-[#202c33] px-3 py-2 text-[13px] leading-snug text-white'
                }
              >
                {m.text}
                {m.from === 'agent' && (
                  <CheckCheck className="mt-0.5 ml-auto h-3 w-3 text-sky-300" />
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Barra de escritura */}
      <div className="flex items-center gap-2 px-3 pb-3">
        <div className="flex-1 rounded-full bg-[#202c33] px-3 py-2 text-[12px] text-white/40">
          Escribe un mensaje…
        </div>
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#00a884]">
          <Mic className="h-4 w-4 text-white" />
        </div>
      </div>
    </div>
  )
}

/** Escena 2: llamada de voz con el agente IA (pantalla de llamada en curso). */
function CallScene() {
  const [secs, setSecs] = useState(0)

  useEffect(() => {
    setSecs(0)
    const id = setInterval(() => setSecs((s) => s + 1), 1000)
    return () => clearInterval(id)
  }, [])

  const mm = String(Math.floor(secs / 60)).padStart(2, '0')
  const ss = String(secs % 60).padStart(2, '0')

  return (
    <div className="flex h-full flex-col bg-gradient-to-b from-[#075e54] via-[#0b5f54] to-[#0a3d36] text-white">
      <StatusBar />
      <div className="flex flex-1 flex-col items-center justify-between py-8">
        <div className="text-center">
          <p className="text-[11px] uppercase tracking-widest text-white/60">Llamada · WhatsApp</p>
          <p className="mt-3 text-xl font-semibold">Tu Negocio</p>
          <p className="mt-1 text-sm text-white/70">Asistente IA · {mm}:{ss}</p>
        </div>

        {/* Avatar con anillos pulsantes */}
        <div className="relative flex items-center justify-center">
          {[0, 1, 2].map((i) => (
            <motion.span
              key={i}
              className="absolute rounded-full border border-white/30"
              initial={{ width: 96, height: 96, opacity: 0.5 }}
              animate={{ width: 200, height: 200, opacity: 0 }}
              transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.8, ease: 'easeOut' }}
            />
          ))}
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-white/15 backdrop-blur-sm">
            <Logo size={56} />
          </div>
        </div>

        {/* Onda de voz animada */}
        <div className="flex items-end gap-1.5">
          {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <motion.span
              key={i}
              className="w-1.5 rounded-full bg-white/80"
              animate={{ height: [8, 26, 12, 30, 10] }}
              transition={{
                duration: 1.1,
                repeat: Infinity,
                delay: i * 0.09,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>

        {/* Botones de llamada */}
        <div className="flex items-center gap-6">
          <CallBtn icon={Mic} label="Silenciar" />
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-500 shadow-lg shadow-red-500/40">
            <PhoneOff className="h-7 w-7 text-white" />
          </div>
          <CallBtn icon={Volume2} label="Altavoz" />
        </div>
      </div>
    </div>
  )
}

function CallBtn({ icon: Icon, label }: { icon: React.ComponentType<{ className?: string }>; label: string }) {
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white/15 backdrop-blur-sm">
        <Icon className="h-5 w-5 text-white" />
      </div>
      <span className="text-[10px] text-white/70">{label}</span>
    </div>
  )
}
