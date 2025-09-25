import { Card, Col, Row, Statistic } from 'antd';
import { MaterialsListItem } from '../../types';

interface MaterialKpiCardsProps {
  materials: MaterialsListItem[];
}

export const MaterialKpiCards: React.FC<MaterialKpiCardsProps> = ({ materials }) => {
  const total = materials.length;
  const active = materials.filter((item) => item.isActive).length;
  const critical = materials.filter((item) => item.isCritical).length;
  const noPrice = materials.filter((item) => !item.price).length;

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} lg={6}>
        <Card bordered className="content-card">
          <Statistic title="Всего материалов" value={total} />
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card bordered className="content-card">
          <Statistic title="Активные" value={active} valueStyle={{ color: '#52c41a' }} />
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card bordered className="content-card">
          <Statistic title="Критичные" value={critical} valueStyle={{ color: '#fa541c' }} />
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card bordered className="content-card">
          <Statistic title="Без цены" value={noPrice} valueStyle={{ color: '#faad14' }} />
        </Card>
      </Col>
    </Row>
  );
};

export default MaterialKpiCards;
