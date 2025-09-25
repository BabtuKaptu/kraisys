import { ConfigProvider, message } from 'antd'
import { screen } from '@testing-library/react'
import { afterEach, beforeAll, beforeEach, vi } from 'vitest'
import { Models } from './Models'
import { renderWithProviders } from '../test-utils'
import { resetMockData } from '../services/mockDataClient'

beforeAll(() => {
  vi.spyOn(message, 'success').mockImplementation(() => ({
    then: () => undefined,
  }) as unknown as ReturnType<typeof message.success>)
  vi.spyOn(message, 'error').mockImplementation(() => ({
    then: () => undefined,
  }) as unknown as ReturnType<typeof message.error>)
})

afterEach(() => {
  vi.clearAllMocks()
})

beforeEach(() => {
  resetMockData()
})

describe('Models page', () => {
  it('renders table with mock data', async () => {
    renderWithProviders(
      <ConfigProvider>
        <Models />
      </ConfigProvider>,
    )

    const cells = await screen.findAllByRole('cell', { name: 'SPORT 250' })
    expect(cells.length).toBeGreaterThan(0)
    expect(screen.getByRole('button', { name: /Добавить модель$/ })).toBeInTheDocument()
  })
})
