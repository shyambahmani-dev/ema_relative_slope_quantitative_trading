<h1>Library Installation</h1>

<p>To ensure a smooth execution of the backtesting program, please follow these steps to install the required dependencies.</p>

<h2>Step 1: Download the Repository</h2>

<p>Clone or download this repository to your local machine.</p>

<pre>
<code>
git clone https://github.com/your_username/your_repository.git
cd your_repository
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

<p>Open the <code>backtest</code> folder and run the <code>ema_slope_rel_L_strat.py</code> script to perform the backtesting of the strategy for NSEI (Nifty 50) for the last 2 years. The program is currently parameterized for performance on NIFTY 50 Index. </p>


<pre>
<code>
cd backtest
python ema_slope_rel_L_strat.py
</code>
</pre>


<p>The script will generate backtesting results and reports in the <code>results</code> folder.</p>
