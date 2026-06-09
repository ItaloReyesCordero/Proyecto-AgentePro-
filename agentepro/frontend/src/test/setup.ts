import '@testing-library/jest-dom/vitest'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

// Limpia el DOM renderizado entre tests para evitar fugas entre casos.
afterEach(() => {
  cleanup()
})
