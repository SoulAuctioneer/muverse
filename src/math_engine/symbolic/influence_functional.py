"""Feynman-Vernon influence functional for the Caldeira-Leggett model.

The influence functional is the *correct* description of how a thermal
bath suppresses quantum paths. It replaces the speculative "decoherence
is a Wick rotation" (axiom A3) with a derivation from first principles.

For a system linearly coupled to a bath of harmonic oscillators:
  H = H_S + Σ_k [p_k²/(2m_k) + m_k ω_k² (x_k − c_k x / m_k ω_k²)² / 2]

The reduced density matrix is:
  ρ(x_f, x_f', t) = ∫ dx_i dx_i' ∫Dx Dx'
    exp(i(S[x] − S[x'])/ℏ) · F[x, x'] · ρ₀(x_i, x_i')

where F[x, x'] = exp(−Φ[x, x']/ℏ) is the Feynman-Vernon influence
functional, and Φ encodes all bath effects.

References:
  Feynman & Vernon, Ann. Phys. 24, 118 (1963)
  Caldeira & Leggett, Ann. Phys. 149, 374 (1983)
  Weiss, "Quantum Dissipative Systems" (World Scientific, 4th ed.)
"""

from __future__ import annotations

import sympy as sp
from sympy import (
    Function,
    I,
    Rational,
    Symbol,
    conjugate,
    cos,
    cot,
    exp,
    integrate,
    oo,
    pi,
    sin,
    sqrt,
    symbols,
)

# Shared symbols
hbar = Symbol(r"\hbar", positive=True)
k_B = Symbol("k_B", positive=True)
beta = Symbol(r"\beta", positive=True)  # 1/(k_B T)
T_phys = Symbol("T", positive=True)
omega = Symbol(r"\omega", positive=True)
omega_c = Symbol(r"\omega_c", positive=True)  # cutoff frequency
gamma_bath = Symbol(r"\gamma", positive=True)  # damping coefficient
lam = Symbol(r"\lambda", positive=True)  # reorganisation energy
m_sys = Symbol("m", positive=True)
t_sym, s_sym = symbols("t s", real=True)
tau = Symbol(r"\tau", positive=True)


def drude_lorentz_spectral_density() -> dict[str, sp.Expr]:
    """Drude-Lorentz (Ohmic with Lorentzian cutoff) spectral density.

    J(ω) = 2λγω / (ω² + γ²)

    This is the standard model for an Ohmic bath with exponential memory.
    At low frequencies J(ω) ≈ 2λω/γ (Ohmic), and the cutoff γ sets the
    bath memory time τ_c = 1/γ.
    """
    J = 2 * lam * gamma_bath * omega / (omega**2 + gamma_bath**2)
    J_ohmic_limit = 2 * lam * omega / gamma_bath
    return {
        "J_omega": J,
        "ohmic_limit": J_ohmic_limit,
        "description": (
            r"J(\omega) = \frac{2\lambda\gamma\omega}{\omega^2 + \gamma^2}"
        ),
        "parameters": {
            "lambda": "reorganisation energy (coupling strength)",
            "gamma": "cutoff frequency (inverse bath memory time)",
        },
    }


def bath_correlation_function() -> dict[str, sp.Expr]:
    r"""Bath correlation function C(t) for a thermal Drude-Lorentz bath.

    C(t) = ∫₀^∞ (dω/π) J(ω) [coth(βℏω/2) cos(ωt) − i sin(ωt)]

    For the Drude-Lorentz spectral density, the correlation function can
    be evaluated via contour integration. The result decomposes into:
      C(t) = C_real(t) + i·C_imag(t)

    where C_real controls decoherence and C_imag controls dissipation.

    At high T (βℏγ ≪ 1): C_real(t) ≈ (2λ/βℏ) e^{−γ|t|}
    """
    nu_1 = 2 * pi / (beta * hbar)  # first Matsubara frequency

    C_real_highT = (2 * lam / (beta * hbar)) * exp(-gamma_bath * sp.Abs(t_sym))

    C_imag = -lam * gamma_bath * exp(-gamma_bath * sp.Abs(t_sym))

    C_real_exact = lam * gamma_bath * (
        sp.cot(beta * hbar * gamma_bath / 2) * exp(-gamma_bath * sp.Abs(t_sym))
    )

    return {
        "C_real_highT": C_real_highT,
        "C_imag": C_imag,
        "C_real_exact_leading": C_real_exact,
        "first_matsubara": nu_1,
        "description": (
            r"C(t) = \int_0^\infty \frac{d\omega}{\pi} J(\omega)"
            r"\left[\coth\frac{\beta\hbar\omega}{2}\cos\omega t "
            r"- i\sin\omega t\right]"
        ),
        "high_T_limit": (
            r"C_{\mathrm{re}}(t) \approx \frac{2\lambda}{\beta\hbar}"
            r"e^{-\gamma|t|}"
        ),
    }


def influence_functional_phase() -> dict[str, sp.Expr]:
    r"""The influence functional phase Φ[x, x'].

    The influence functional is F[x, x'] = exp(−Φ[x, x']/ℏ), where:

    Φ = (1/ℏ) ∫₀^t ds ∫₀^s ds' Δ(s) [C_re(s−s') Δ(s') + i C_im(s−s') Σ(s')]

    with path-difference coordinates:
      Δ(s) = x(s) − x'(s)     (difference)
      Σ(s) = x(s) + x'(s)     (centre-of-mass)

    Physical interpretation:
      Re(Φ): decoherence — suppresses paths where x ≠ x'
      Im(Φ): dissipation — shifts the potential (friction)

    CRITICAL OBSERVATION: Φ depends on the PATH DIFFERENCE Δ and the
    bath correlation C(t), NOT on the Euclidean action S_E of a single
    path. The "Wick rotation" axiom A3 conflates these.
    """
    Delta, Sigma = symbols(r"\Delta \Sigma", cls=Function)

    C_re = Function("C_re")
    C_im = Function("C_im")

    Phi_integrand = Delta(s_sym) * (
        C_re(t_sym - s_sym) * Delta(s_sym) + I * C_im(t_sym - s_sym) * Sigma(s_sym)
    )

    return {
        "Phi_integrand": Phi_integrand,
        "influence_functional": exp(-Symbol(r"\Phi") / hbar),
        "description": (
            r"\Phi[x,x'] = \frac{1}{\hbar}\int_0^t ds \int_0^s ds'\,"
            r"\Delta(s)\left[C_{\mathrm{re}}(s-s')\Delta(s') "
            r"+ i\,C_{\mathrm{im}}(s-s')\Sigma(s')\right]"
        ),
        "Re_Phi_role": "decoherence: suppresses path separations Δ = x − x'",
        "Im_Phi_role": "dissipation: renormalises the system potential (friction)",
        "critical_distinction": (
            "Φ depends on the path difference Δ(t) = x(t) − x'(t) and the "
            "bath correlation C(t), NOT on the Euclidean action S_E of a "
            "single path. This is why 'decoherence = Wick rotation' (A3) "
            "is a category error: the suppression mechanism is fundamentally "
            "about path coherence, not about imaginary-time continuation."
        ),
    }


def high_T_ohmic_limit() -> dict[str, sp.Expr]:
    r"""The Caldeira-Leggett high-T limit.

    At high temperature (k_BT ≫ ℏγ), the real part of the influence
    functional phase becomes:

      Re(Φ) ≈ (2mγk_BT/ℏ²) ∫₀^t ds [x(s) − x'(s)]²

    This is:
      1. LOCAL in time (no memory)
      2. Quadratic in the path separation
      3. Proportional to temperature × friction

    This is the Caldeira-Leggett decoherence rate. It suppresses
    superpositions of spatially separated states, but the suppression
    depends on spatial separation, NOT on the Euclidean action.

    The connection to statistical mechanics comes from the DISSIPATION
    part (Im Φ), which produces a friction force that drives the system
    toward the Gibbs state exp(−βH)/Z — over ENERGIES, not actions.
    """
    x, x_prime = symbols("x x'")
    Delta_sq = (x - x_prime) ** 2

    Gamma_decoherence = 2 * m_sys * gamma_bath * k_B * T_phys / hbar**2

    Re_Phi_local = Gamma_decoherence * Delta_sq

    return {
        "decoherence_rate": Gamma_decoherence,
        "Re_Phi_local": Re_Phi_local,
        "description": (
            r"\mathrm{Re}(\Phi) \approx \frac{2m\gamma k_BT}{\hbar^2}"
            r"\int_0^t ds\,[x(s) - x'(s)]^2"
        ),
        "physical_meaning": (
            "Decoherence rate Γ = 2mγk_BT/ℏ² suppresses superpositions "
            "of spatially separated states. The suppression is local in "
            "time (Markovian), quadratic in path separation, and "
            "proportional to T×γ. It has NO dependence on the Euclidean "
            "action S_E."
        ),
        "what_drives_equilibrium": (
            "The dissipative part Im(Φ) produces friction that drives the "
            "system toward the Gibbs state exp(−βE)/Z — weighting by "
            "ENERGY, not by Euclidean action."
        ),
    }


def mean_force_gibbs_state() -> dict[str, sp.Expr]:
    r"""The mean-force Gibbs state: the exact steady state at any coupling.

    For a system coupled to an equilibrium bath, the exact reduced steady
    state is NOT exp(−βH_S)/Z but:

      ρ_MF = exp(−β H_MF) / Z_MF

    where H_MF = −T log Tr_B[exp(−β H_total)] is the Hamiltonian of mean
    force. At weak coupling H_MF → H_S (bare system). At strong coupling
    H_MF includes bath-induced corrections:

      H_MF = H_S + Δ_Lamb + O(λ²)

    where Δ_Lamb is the Lamb shift (potential renormalisation).

    The key question for Thermodynamic Darwinism: does H_MF at strong
    coupling correlate with the WKB tunneling actions S_E? The answer is
    a numerical question, addressed by Simulation 6 (HEOM).
    """
    H_S = Symbol("H_S")
    H_MF = Symbol("H_{MF}")
    Delta_Lamb = Symbol(r"\Delta_{\mathrm{Lamb}}")
    Z_MF = Symbol("Z_{MF}")

    rho_MF = exp(-beta * H_MF) / Z_MF

    return {
        "rho_MF": rho_MF,
        "H_MF_expansion": H_S + Delta_Lamb,
        "description": (
            r"\rho_{\mathrm{MF}} = \frac{e^{-\beta H_{\mathrm{MF}}}}"
            r"{Z_{\mathrm{MF}}}, \quad "
            r"H_{\mathrm{MF}} = -T\ln\mathrm{Tr}_B\!\left["
            r"e^{-\beta H_{\mathrm{total}}}\right]"
        ),
        "weak_coupling_limit": (
            r"H_{\mathrm{MF}} \to H_S \implies "
            r"\rho_{\mathrm{MF}} \to e^{-\beta H_S}/Z "
            r"\text{ (confirmed by Sim5 Lindblad)}"
        ),
        "strong_coupling": (
            r"H_{\mathrm{MF}} = H_S + \Delta_{\mathrm{Lamb}} "
            r"+ \mathcal{O}(\lambda^2). "
            r"\text{The steady state deviates from bare Gibbs.}"
        ),
        "key_question": (
            "Does the strong-coupling correction to the steady state "
            "correlate with the WKB tunneling actions? Simulation 6 "
            "(HEOM) tests this numerically."
        ),
    }
