import React from 'react';
import mqtt from 'mqtt/dist/mqtt.min';
import HeatMap from 'react-heatmap-grid';
import { useEffect } from 'react';
import { create, all } from 'mathjs';
import Plot from 'react-plotly.js';

const config = {
  epsilon: 1e-12,
  matrix: 'Matrix',
  number: 'number',
  precision: 64,
  predictable: false,
  randomSeed: null,
};
const math = create(all, config);

var colorscale = [
  ['0.0', 'rgb(49,54,149)'],
  ['0.111111111111', 'rgb(69,117,180)'],
  ['0.222222222222', 'rgb(116,173,209)'],
  ['0.333333333333', 'rgb(171,217,233)'],
  ['0.444444444444', 'rgb(224,243,248)'],
  ['0.555555555556', 'rgb(254,224,144)'],
  ['0.666666666667', 'rgb(253,174,97)'],
  ['0.777777777778', 'rgb(244,109,67)'],
  ['0.888888888889', 'rgb(215,48,39)'],
  ['1.0', 'rgb(165,0,38)'],
];

const options = {
  username: 'proto',
  password: 'workz',
  keepalive: 60,
};

export const NormalMqtt = () => {
  const [currentMessage, setCurrentMessage] = React.useState(null);

  useEffect(() => {
    const client = mqtt.connect('ws://77.161.23.64:9001', options);
    client.on('connect', function () {
      client.subscribe('temperature', function (err) {
        if (!err) {
          console.log('HIER GAAT IETS NIET GOED!');
        }
      });
    });

    client.on('message', function (topic, message) {
      const messageSplitted = message.toString().split(',');
      messageSplitted.pop();

      const msgArray = messageSplitted.map((x) => {
        return (x - 20) / (40 - 20);
      });

      const newMsg = math.reshape(msgArray, [24, 32]);

      setCurrentMessage(newMsg);
      console.log(currentMessage);
      client.end();
    });
  });

  return (
    <>
      {currentMessage !== null ? (
        <Plot
          data={[
            {
              z: currentMessage,
              x: [],
              type: 'heatmap',
              colorscale: colorscale,
              labels: false,
            },
          ]}
          layout={{ height: 1080, width: 1440, showlegend: false }}
        />
      ) : (
        <div>Loading...</div>
      )}
    </>
  );
};
