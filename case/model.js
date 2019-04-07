const React = require("react");
const {
  Model,
  Cube,
  Subtract
} = require("../../../modeler/packages/modeler-csg");

const range = n => Array.from({ length: n }).map((_, i) => i);

// in CM
const MONOME_SIZE = [24, 12];
const PLATE_HEIGHT = 0.5;

const MonomeBase = () => (
  <Cube
    radius={[MONOME_SIZE[0] / 2, PLATE_HEIGHT / 2, MONOME_SIZE[1] / 2]}
    center={[0, PLATE_HEIGHT / 2, 0]}
  />
);

module.exports = () => (
  <Model>
    <Subtract>
      <MonomeBase />
      {range(16).map(i =>
        range(8).map(j => {
          const size = 1;
          const x = -MONOME_SIZE[0] / 2 + size / 2 + 0.2 + i * (size + 0.5);
          const y = -MONOME_SIZE[1] / 2 + size / 2 + 0.2 + j * (size + 0.5);

          return (
            <Cube
              key={`${i}-${j}`}
              radius={size / 2}
              center={[x, size / 2, y]}
            />
          );
        })
      )}
    </Subtract>
  </Model>
);
