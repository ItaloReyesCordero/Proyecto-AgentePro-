import { LegalLayout, LegalSection } from './LegalLayout'

const CONTACT_EMAIL = 'italoreyescordero1@gmail.com'
const CONTACT_WHATSAPP = '+51 916 085 873'
const TITULAR = 'Italo Eduardo Reyes Cordero'

/**
 * Términos y Condiciones del servicio. Refleja el modelo de negocio real:
 * 14 días gratis + pago mensual POR ADELANTADO vía Yape/transferencia (sin pasarela).
 * NOTA: base sólida; conviene revisión legal antes de producción.
 */
export function TermsPage() {
  return (
    <LegalLayout title="Términos y Condiciones" updated="3 de junio de 2026">
      <p>
        Estos Términos regulan el uso de <strong className="text-text-primary">AgentePro</strong>,
        plataforma de automatización de atención al cliente con inteligencia artificial operada por{' '}
        {TITULAR} en Perú. Al crear una cuenta o usar el servicio, aceptas estos Términos.
      </p>

      <LegalSection title="1. Descripción del servicio">
        <p>
          AgentePro provee un agente de IA que atiende los canales de mensajería (WhatsApp, Instagram) y,
          opcionalmente, llamadas de voz de un negocio: responde consultas, califica clientes potenciales,
          agenda citas y muestra métricas. El alcance depende del plan contratado.
        </p>
      </LegalSection>

      <LegalSection title="2. Cuenta y responsabilidad del cliente">
        <ul className="list-disc space-y-1 pl-5">
          <li>Eres responsable de la veracidad de los datos que registras y de la custodia de tu contraseña.</li>
          <li>Eres responsable del contenido y la configuración que le das a tu agente, y de cumplir las leyes aplicables a tu negocio.</li>
          <li>Te comprometes a usar el servicio de forma lícita y a no enviar spam ni mensajes no solicitados, respetando las políticas de WhatsApp/Meta.</li>
        </ul>
      </LegalSection>

      <LegalSection title="3. Prueba gratuita de 14 días">
        <p>
          Las cuentas nuevas inician con una <strong className="text-text-primary">prueba gratuita de 14
          días</strong>, con acceso a las funciones del plan elegido y sin necesidad de tarjeta. Al
          terminar la prueba, para continuar usando el servicio deberás activar un plan de pago.
        </p>
      </LegalSection>

      <LegalSection title="4. Planes, precios y pago por adelantado">
        <p>Los planes mensuales vigentes son:</p>
        <ul className="list-disc space-y-1 pl-5">
          <li><strong className="text-text-primary">Inicial:</strong> S/ 149 al mes.</li>
          <li><strong className="text-text-primary">Basic:</strong> S/ 249 al mes.</li>
          <li><strong className="text-text-primary">Professional:</strong> S/ 449 al mes.</li>
          <li><strong className="text-text-primary">Enterprise:</strong> S/ 799 al mes.</li>
        </ul>
        <p>
          El pago es <strong className="text-text-primary">mensual y por adelantado</strong>, mediante{' '}
          <strong className="text-text-primary">Yape o transferencia</strong> a los datos que te
          indicamos. Una vez confirmado tu pago, tu servicio queda activo por un mes más. Los precios
          pueden actualizarse avisándote con anticipación.
        </p>
      </LegalSection>

      <LegalSection title="5. Falta de pago y suspensión">
        <p>
          Si no recibimos tu pago en la fecha de vencimiento, tu servicio puede{' '}
          <strong className="text-text-primary">suspenderse</strong>: el agente deja de responder y el
          panel queda bloqueado hasta regularizar. <strong className="text-text-primary">Tus datos se
          conservan</strong> durante la suspensión y se reactivan al confirmar el pago. Tú puedes cancelar
          cuando quieras; al no ser un pago automático, basta con no renovar.
        </p>
      </LegalSection>

      <LegalSection title="6. Disponibilidad y servicios de terceros">
        <p>
          Hacemos un esfuerzo razonable por mantener el servicio disponible, pero depende de proveedores
          externos (Meta/WhatsApp, Anthropic, Twilio, Retell, hosting). No garantizamos disponibilidad
          ininterrumpida y no somos responsables por fallas o cambios de esos terceros ajenos a nosotros.
        </p>
      </LegalSection>

      <LegalSection title="7. Uso de inteligencia artificial">
        <p>
          Las respuestas las genera un modelo de IA configurado por el negocio. Aunque buscamos calidad,
          la IA puede cometer errores. El negocio puede tomar el control de cualquier conversación y es
          responsable de supervisar el uso del agente con sus clientes.
        </p>
      </LegalSection>

      <LegalSection title="8. Propiedad intelectual">
        <p>
          El software, la marca y el código de AgentePro son propiedad de {TITULAR} y están protegidos por
          derechos de autor. Se te otorga una licencia de uso mientras tengas una cuenta activa; no puedes
          copiar, revender ni redistribuir la plataforma. El contenido y los datos de tu negocio siguen
          siendo tuyos.
        </p>
      </LegalSection>

      <LegalSection title="9. Limitación de responsabilidad">
        <p>
          En la medida permitida por la ley, AgentePro no será responsable por daños indirectos o lucro
          cesante derivados del uso o imposibilidad de uso del servicio. Nuestra responsabilidad máxima se
          limita al monto pagado por el cliente en el último mes.
        </p>
      </LegalSection>

      <LegalSection title="10. Cambios y ley aplicable">
        <p>
          Podemos actualizar estos Términos; publicaremos la versión vigente en esta página. Estos
          Términos se rigen por las leyes de la República del Perú.
        </p>
      </LegalSection>

      <LegalSection title="11. Contacto">
        <p>
          ¿Consultas? Escríbenos a{' '}
          <a className="text-primary hover:underline" href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>{' '}
          o por WhatsApp al {CONTACT_WHATSAPP}.
        </p>
      </LegalSection>
    </LegalLayout>
  )
}
