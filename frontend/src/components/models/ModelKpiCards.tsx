import { Card, Col, Row, Statistic, Tag, Tooltip } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { ModelListItem } from '../../types';

interface ModelKpiCardsProps {
  models: ModelListItem[];
}

const defaultKpi = (models: ModelListItem[]) => ({
  total: models.length,
  active: models.filter((model) => model.status === 'ACTIVE').length,
  inactive: models.filter((model) => model.status !== 'ACTIVE').length,
  latestUpdated: models
    .slice()
    .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
    .slice(0, 1)
    .map((item) => item.name)[0],
});

export const ModelKpiCards: React.FC<ModelKpiCardsProps> = ({ models }) => {
  const { total, active, inactive, latestUpdated } = defaultKpi(models);
  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} lg={6}>
        <Card bordered className="content-card">
          <Statistic title="Всего моделей" value={total} />
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card bordered className="content-card">
          <Statistic title="Активные" value={active} valueStyle={{ color: '#52c41a' }} />
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card bordered className="content-card">
          <Statistic title="Архив" value={inactive} valueStyle={{ color: '#faad14' }} />
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card bordered className="content-card">
          <Statistic
            title={
              <span>
                Последнее обновление{' '}
                <Tooltip title="Модель, изменённая последней">
                  <InfoCircleOutlined />
                </Tooltip>
              </span>
            }
            value={latestUpdated ?? '—'}
            formatter={(value) => (
              <Tag color="blue" style={{ marginInline: 0 }}>
                {value}
              </Tag>
            )}
          />
        </Card>
      </Col>
    </Row>
  );
};
