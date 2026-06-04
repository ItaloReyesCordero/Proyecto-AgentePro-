import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'

/**
 * Campo de contraseña con botón de "ojito" para ver/ocultar lo escrito.
 * Acepta las mismas props que un <input> normal (value, onChange, required,
 * minLength, placeholder, etc.). Reutilizable en login, registro y admin.
 */
export function PasswordInput({
  className = 'input-base',
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  const [show, setShow] = useState(false)
  return (
    <div className="relative">
      <input
        {...props}
        type={show ? 'text' : 'password'}
        className={`${className} pr-10`}
      />
      <button
        type="button"
        tabIndex={-1}
        onClick={() => setShow((s) => !s)}
        aria-label={show ? 'Ocultar contraseña' : 'Mostrar contraseña'}
        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-secondary transition hover:text-text-primary"
      >
        {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
      </button>
    </div>
  )
}
