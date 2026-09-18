# mm_sim.py
import numpy as np
import matplotlib.pyplot as plt

def simulate(spread=1.0, skew_k=0.0, n=5000, limit=20, seed=0):
    rng = np.random.default_rng(seed)
    fair, inv, cash = 100.0, 0, 0.0
    kappa, sigma, mu = 0.05, 0.3, 100.0    # 公允价：OU 均值回复
    A, decay = 0.9, 1.2                    # 成交概率：离公允价越远越难成交

    pnl, invs = [], []
    for _ in range(n):
        fair += kappa * (mu - fair) + sigma * rng.standard_normal()

        center = fair - skew_k * inv       # 
        bid, ask = center - spread/2, center + spread/2

        p_bid = np.clip(A * np.exp(-decay * (fair - bid)), 0, 1)
        p_ask = np.clip(A * np.exp(-decay * (ask - fair)), 0, 1)

        if rng.random() < p_bid and inv < limit:
            inv += 1; cash -= bid
        if rng.random() < p_ask and inv > -limit:
            inv -= 1; cash += ask

        pnl.append(cash + inv * fair)      # mark-to-market PnL
        invs.append(inv)
    return np.array(pnl), np.array(invs)


def evaluate(spread, skew_k, seeds=200):
    finals, sharpes, maxinv = [], [], []
    for s in range(seeds):
        p, i = simulate(spread=spread, skew_k=skew_k, seed=s)
        d = np.diff(p)
        finals.append(p[-1])
        sharpes.append(d.mean() / (d.std() + 1e-9) * np.sqrt(len(d)))
        maxinv.append(np.abs(i).max())
    print(f"spread={spread:.1f} skew={skew_k:.3f} | "
          f"PnL={np.mean(finals):7.1f} ± {np.std(finals):6.1f} | "
          f"Sharpe={np.mean(sharpes):5.2f} | max|inv|={np.mean(maxinv):5.1f}")


print("=== 对称报价 vs 库存偏斜 ===")
for k in [0.0, 0.02, 0.05, 0.10, 0.20]:
    evaluate(1.0, k)

print("\n=== 价差扫描 (skew=0.05) ===")
for sp in [0.4, 0.8, 1.2, 1.6, 2.0, 3.0]:
    evaluate(sp, 0.05)

# 出图
plt.figure(figsize=(10,4))
for k in [0.0, 0.05]:
    p, i = simulate(skew_k=k, seed=7)
    plt.subplot(1,2,1); plt.plot(p, label=f"skew={k}")
    plt.subplot(1,2,2); plt.plot(i, label=f"skew={k}")
plt.subplot(1,2,1); plt.title("PnL"); plt.legend()
plt.subplot(1,2,2); plt.title("Inventory"); plt.legend()
plt.tight_layout(); plt.savefig("pnl.png", dpi=120); plt.show()