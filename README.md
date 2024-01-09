<h1>Library Installation</h1>

<p>To ensure a smooth execution of the backtesting program, please follow these steps to install the required dependencies.</p>

<h2>Step 1: Download the Repository</h2>

<p>Clone or download this repository to your local machine.</p>

<pre>
<code>
git clone https://shyambahmani-dev/relative_ema_slope_quantitative_trading.git
cd relative_ema_slope_quantitative_trading
cd Project1
</code>
</pre>

<h2>Step 2: Run Dependency Installation Script</h2>

<p>Execute the <code>libs_install.py</code> script to automatically install the necessary dependencies. This script will utilize <code>pip</code>, the Python package installer, to fetch and install the required libraries.</p>

<pre>
<code>
python libs_install.py
</code>
</pre>

<p><code>Note: Ensure that you have Python and pip installed on your machine.</code></p>



<h2>Step 3: Backtesting the Strategy</h2>

<p>Open the <code>backtest</code> folder. There are currently 2 strategies. One <code>ema_slope_rel_L_strat.py</code> using 1 indicator for buy-sell signal generation, and another <code>ema_slope_rel_2S_L_strat.py</code> using 2 indicators for buy-sell signal generation. Run the desired script to perform the backtesting of the strategy for NSEI (Nifty 50) for the last 2 years. The program is currently parameterized for performance on NIFTY 50 Index. Run the </p>


<pre>
<code>
cd backtest
python ema_slope_rel_2S_L_strat.py

## -- 1 indicator per signal strategy -- ##

cd backtest
python ema_slope_rel_L_strat.py


</code>
</pre>


<p>The models will generate backtesting results and reports in the <code>results</code> folder.</p>
<p>The models use backtesting data from 2021-2023 for optimizing the signal parameters. If the strategy is not generating alpha, use the <code>ema_rel_slope_L_strat_func.py</code> to re-evaluate the optimal parameters for signals (1 Indicator signal generation), subject to current market conditions</p>
