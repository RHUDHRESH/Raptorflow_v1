import { render, screen } from '@testing-library/react'
import { describe, it, expect } from '@jest/globals'

// Example test component
const ExampleComponent = () => {
  return <div>Test Component</div>
}

describe('ExampleComponent', () => {
  it('renders correctly', () => {
    render(<ExampleComponent />)
    expect(screen.getByText('Test Component')).toBeInTheDocument()
  })
})
