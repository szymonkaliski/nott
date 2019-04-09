const React = require("react");
const {
  Model,
  Cube,
  Subtract,
  Cylinder
} = require("../../../modeler/packages/modeler-csg");

const range = n => Array.from({ length: n }).map((_, i) => i);

const RENDER_HOLES = process.env.RENDER_HOLES
  ? process.env.RENDER_HOLES === "true"
  : true;

// in CM
const MONOME_SIZE = [24, 12];
const TOP_SIZE = [MONOME_SIZE[0], 5.5];
const PLATE_MARGIN = 0.5;
const PLATE_HEIGHT = 0.25;

const TopPlate = () => (
  <Cube
    radius={[
      MONOME_SIZE[0] / 2 + PLATE_MARGIN,
      PLATE_HEIGHT / 2,
      (TOP_SIZE[1] + MONOME_SIZE[1]) / 2 + PLATE_MARGIN
    ]}
    position={[0, , 0]}
    center={[0, PLATE_HEIGHT / 2]}
  />
);

const Dial = ({ yOffset }) => {
  const r = 0.7 / 2;
  const x = MONOME_SIZE[0] / 2 - 6.8;
  const y = -(MONOME_SIZE[1] + TOP_SIZE[1]) / 2 + yOffset;

  return <Cylinder radius={r} start={[x, 0, y]} end={[x, 1, y]} />;
};

module.exports = () => (
  <Model>
    <Subtract>
      <TopPlate />

      {/* buttons */}
      {RENDER_HOLES &&
        range(16).map(i =>
          range(8).map(j => {
            const size = 1;
            const x = -MONOME_SIZE[0] / 2 + size / 2 + 0.2 + i * (size + 0.5);
            const y =
              -MONOME_SIZE[1] / 2 +
              size / 2 +
              0.2 +
              j * (size + 0.5) +
              TOP_SIZE[1] / 2;

            return (
              <Cube
                key={`${i}-${j}`}
                radius={size / 2}
                center={[x, size / 2, y]}
              />
            );
          })
        )}

      {/* monome screws */}
      {RENDER_HOLES &&
        range(8).map(i =>
          range(4).map(j => {
            const r = 0.2;
            const x = -MONOME_SIZE[0] / 2 + 1.45 + i * 3;
            const y = -MONOME_SIZE[1] / 2 + 1.45 + j * 3 + TOP_SIZE[1] / 2;

            return (
              <Cylinder radius={r / 2} start={[x, 0, y]} end={[x, 1, y]} />
            );
          })
        )}

      {/* dials */}
      {RENDER_HOLES && [1.7, 3.7].map(offset => <Dial yOffset={offset} />)}

      {/* plate screws */}
      {[
        [-0.25, -0.25],
        [-0.25, MONOME_SIZE[1] + TOP_SIZE[1] + 0.25],
        [MONOME_SIZE[0] + 0.25, -0.25],
        [MONOME_SIZE[0] + 0.25, MONOME_SIZE[1] + TOP_SIZE[1] + 0.25]
      ].map(([ox, oy]) => {
        const r = 0.2;

        const x = -MONOME_SIZE[0] / 2 + ox;
        const y = -(MONOME_SIZE[1] + TOP_SIZE[1]) / 2 + oy;

        return <Cylinder radius={r / 2} start={[x, 0, y]} end={[x, 1, y]} />;
      })}
    </Subtract>
  </Model>
);
