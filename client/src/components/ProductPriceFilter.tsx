import React, { useState } from 'react';

type Props = {
  onFilter: (min: number | null, max: number | null) => void;
};

const ProductPriceFilter: React.FC<Props> = ({ onFilter }) => {
  const [min, setMin] = useState<number | ''>('');
  const [max, setMax] = useState<number | ''>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilter(min === '' ? null : Number(min), max === '' ? null : Number(max));
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 16 }}>
      <label>
        Цена от:
        <input
          type="number"
          value={min}
          onChange={e => setMin(e.target.value === '' ? '' : Number(e.target.value))}
          min={0}
        />
      </label>
      <label style={{ marginLeft: 8 }}>
        до:
        <input
          type="number"
          value={max}
          onChange={e => setMax(e.target.value === '' ? '' : Number(e.target.value))}
          min={0}
        />
      </label>
      <button type="submit" style={{ marginLeft: 8 }}>Фильтровать</button>
    </form>
  );
};

export default ProductPriceFilter; 