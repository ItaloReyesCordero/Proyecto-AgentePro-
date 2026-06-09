import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { Skeleton, SkeletonCard } from './Skeleton'

describe('Skeleton', () => {
  it('renderiza con la clase pasada', () => {
    const { container } = render(<Skeleton className="h-4 w-32" />)
    expect(container.firstChild).toHaveClass('h-4', 'w-32')
  })

  it('SkeletonCard renderiza varias barras', () => {
    const { container } = render(<SkeletonCard className="mt-2" />)
    expect(container.firstChild).toHaveClass('mt-2')
    expect(container.querySelectorAll('div').length).toBeGreaterThan(1)
  })
})
