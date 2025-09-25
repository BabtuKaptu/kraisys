import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ConfigProvider } from 'antd'
import { vi } from 'vitest'
import { ModelDrawer } from './ModelDrawer'
import { renderWithProviders } from '../../test-utils'

const noop = () => {}

describe('ModelDrawer', () => {
  it('shows basic tabs and validates required fields', async () => {
    const handleSubmit = vi.fn().mockResolvedValue(undefined)

    renderWithProviders(
      <ConfigProvider>
        <ModelDrawer open loading={false} onClose={noop} onSubmit={handleSubmit} onManageVariants={noop} />
      </ConfigProvider>,
    )

    await waitFor(() => expect(screen.getByText('Ценообразование')).toBeInTheDocument())

    const saveButton = screen.getByRole('button', { name: 'Сохранить' })
    await userEvent.click(saveButton)

    await waitFor(() => expect(screen.getByText('Укажите название')).toBeInTheDocument())
    expect(handleSubmit).not.toHaveBeenCalled()
  })
})
