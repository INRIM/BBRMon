# BBRMon

An almost real time monitor of the blackbody radiation (BBR) shift in the optical clock IT-Yb1.

It reads the temperature from sensors and calculate the shift in real time (latency 80 s).
The atomic coefficients used are those for Yb atoms.

## Basic usage

Running the script will open a  `matplotlib' figure that will update in real time.
The script can be left running. To turn off the script simply close the figure.

## Requirements

The script requires the following python packages:
- `numpy`, `scipy`, `matplotlib`
- [`pyvisa`](https://pyvisa.readthedocs.io/en/latest/)

It is set-up to read 10 Pt-1000 platinum resistance thermometers using an Agilent 34970A digital multimiter.
Connection to the instrument is hard-coded.

## Screenshot

![screenshot](https://github.com/INRIM/BBRMon/blob/main/screenshot.png)

## How to cite 

If you find this useful, please cite our original paper:

Pizzocaro, Bregolin, Barbieri,  Rauf,  Levi, & Calonico, [Absolute frequency measurement of the 1S0-3P0 transition of 171Yb with a link to international atomic time](http://doi.org/10.1088/1681-7575/ab50e8), Metrologia **57**, 035007 (2020)

## Acknowledgments
We acknowledge funding from the European Metrology Program for Innovation and Research (EMPIR) project 18SIB05 ROCIT.
The EMPIR initiative is cofunded by the European Union’s Horizon 2020 research and innovation programme and the EMPIR Participating States.

## License

[MIT](https://opensource.org/licenses/MIT)

## Authors

(c) 2021 Marco Pizzocaro - Istituto Nazionale di Ricerca Metrologica (INRIM)
