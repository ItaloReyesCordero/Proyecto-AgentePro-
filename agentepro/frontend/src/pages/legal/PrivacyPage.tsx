import { LegalLayout, LegalSection } from './LegalLayout'

const CONTACT_EMAIL = 'italoreyescordero1@gmail.com'
const CONTACT_WHATSAPP = '+51 916 085 873'
const TITULAR = 'Italo Eduardo Reyes Cordero'

/**
 * Política de Privacidad pública. Meta/WhatsApp exige una URL pública que
 * explique cómo se tratan los datos para aprobar la conexión de WhatsApp Cloud API.
 * Cumple en lo aplicable con la Ley N.° 29733 (Perú) de Protección de Datos Personales.
 * NOTA: es una base sólida; conviene que un abogado la revise antes de producción.
 */
export function PrivacyPage() {
  return (
    <LegalLayout title="Política de Privacidad" updated="3 de junio de 2026">
      <p>
        En <strong className="text-text-primary">AgentePro</strong> ("nosotros", "la plataforma"),
        operado por {TITULAR} en Perú, valoramos y protegemos la privacidad de los datos personales
        tanto de nuestros clientes (los negocios que usan la plataforma) como de las personas que
        conversan con esos negocios a través de nuestros agentes de IA. Esta política explica qué
        datos tratamos, con qué fin y cuáles son tus derechos.
      </p>

      <LegalSection title="1. Responsable del tratamiento">
        <p>
          El responsable es <strong className="text-text-primary">{TITULAR}</strong>. Para cualquier
          consulta sobre tus datos puedes escribirnos a{' '}
          <a className="text-primary hover:underline" href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>{' '}
          o por WhatsApp al {CONTACT_WHATSAPP}.
        </p>
      </LegalSection>

      <LegalSection title="2. Qué datos recopilamos">
        <p>Tratamos dos tipos de datos:</p>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            <strong className="text-text-primary">Datos del negocio cliente:</strong> nombre del negocio,
            nombre y datos de contacto del dueño (correo, teléfono), credenciales de acceso (la contraseña
            se guarda cifrada) y la configuración de su agente.
          </li>
          <li>
            <strong className="text-text-primary">Datos de las conversaciones:</strong> cuando una persona
            escribe al WhatsApp o Instagram de un negocio, procesamos su número/identificador, su nombre de
            perfil y el contenido de los mensajes para poder responder y dar seguimiento (contactos, leads,
            historial de conversación, llamadas y sus transcripciones/resúmenes).
          </li>
          <li>
            <strong className="text-text-primary">Datos técnicos:</strong> registros de uso del sistema
            (logs) necesarios para operar, depurar y mantener la seguridad.
          </li>
        </ul>
      </LegalSection>

      <LegalSection title="3. Para qué usamos los datos">
        <ul className="list-disc space-y-1 pl-5">
          <li>Permitir que el agente de IA responda a los clientes del negocio 24/7.</li>
          <li>Calificar leads, agendar citas y dar seguimiento a las conversaciones.</li>
          <li>Mostrar al negocio sus métricas, conversaciones y contactos.</li>
          <li>Operar, asegurar y mejorar la plataforma.</li>
          <li>Gestionar la facturación del servicio con el negocio.</li>
        </ul>
        <p>
          <strong className="text-text-primary">No vendemos tus datos</strong> ni los usamos para
          publicidad de terceros.
        </p>
      </LegalSection>

      <LegalSection title="4. Datos de WhatsApp e Instagram (Meta)">
        <p>
          La plataforma se integra con la API de WhatsApp Business e Instagram de Meta. Los mensajes que
          una persona envía al negocio se procesan únicamente para prestar el servicio de atención de ese
          negocio. El uso de estos datos cumple con las políticas de Meta. El contenido de las
          conversaciones pertenece al negocio cliente, que actúa como responsable de los datos de sus
          propios clientes; AgentePro los trata por encargo de dicho negocio.
        </p>
      </LegalSection>

      <LegalSection title="5. Con quién compartimos datos (encargados)">
        <p>
          Para funcionar, compartimos lo mínimo necesario con proveedores tecnológicos que actúan como
          encargados del tratamiento bajo sus propias políticas de seguridad:
        </p>
        <ul className="list-disc space-y-1 pl-5">
          <li><strong className="text-text-primary">Anthropic (Claude):</strong> genera las respuestas de IA.</li>
          <li><strong className="text-text-primary">Meta:</strong> envío y recepción de mensajes de WhatsApp/Instagram.</li>
          <li><strong className="text-text-primary">Twilio y Retell:</strong> llamadas de voz (cuando el negocio las usa).</li>
          <li><strong className="text-text-primary">Proveedor de hosting/base de datos:</strong> almacenamiento seguro.</li>
        </ul>
        <p>No compartimos datos con terceros para fines distintos a la prestación del servicio.</p>
      </LegalSection>

      <LegalSection title="6. Conservación de los datos">
        <p>
          Conservamos los datos mientras el negocio mantenga su cuenta activa y por el tiempo necesario
          para cumplir obligaciones legales. Cuando un negocio se da de baja, sus datos pueden eliminarse
          o exportarse a su solicitud.
        </p>
      </LegalSection>

      <LegalSection title="7. Seguridad">
        <p>
          Aplicamos medidas técnicas y organizativas razonables: contraseñas cifradas, aislamiento de los
          datos de cada negocio, control de acceso, cifrado de tokens sensibles y copias de seguridad
          periódicas. Ningún sistema es 100% infalible, pero trabajamos para proteger tu información.
        </p>
      </LegalSection>

      <LegalSection title="8. Tus derechos (Ley N.° 29733 - Perú)">
        <p>
          Tienes derecho a acceder, rectificar, actualizar, oponerte y solicitar la eliminación de tus
          datos personales. Para ejercerlos, escríbenos a{' '}
          <a className="text-primary hover:underline" href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
          Si la consulta proviene de un cliente final de un negocio, lo derivaremos al negocio
          correspondiente, que es el responsable de esos datos.
        </p>
      </LegalSection>

      <LegalSection title="9. Cambios a esta política">
        <p>
          Podemos actualizar esta política. Publicaremos siempre la versión vigente en esta página con su
          fecha de actualización.
        </p>
      </LegalSection>

      <LegalSection title="10. Contacto">
        <p>
          ¿Dudas sobre tu privacidad? Escríbenos a{' '}
          <a className="text-primary hover:underline" href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>{' '}
          o por WhatsApp al {CONTACT_WHATSAPP}.
        </p>
      </LegalSection>
    </LegalLayout>
  )
}
