**Maximin Robust Bayesian Experimental Design** 

**Hany Abdulsamad**[1] **Sahel Iqbal**[2] **Christian A. Naesseth**[1] **Takuo Matsubara**[3] **Adrien Corenflos**[4] 

## **Abstract** 

We address the brittleness of Bayesian experimental design under model misspecification by formulating the problem as a max–min game between the experimenter and an adversarial nature subject to information-theoretic constraints. We demonstrate that this approach yields a robust objective governed by Sibson’s _α_ -mutual information (MI), which identifies the _α_ -tilted posterior as the robust belief update and establishes the Renyi divergence´ as the appropriate measure of conditional information gain. To mitigate the bias and variance of nested Monte Carlo estimators needed to estimate Sibson’s _α_ -MI, we adopt a PAC-Bayes framework to search over stochastic design policies, yielding rigorous high-probability lower bounds on the robust expected information gain that explicitly control finite-sample error. 

## **1. Introduction** 

Experimental design is a foundational component of scientific and engineering inquiry, enabling efficient knowledge acquisition across a wide range of domains including physics, epidemiology, neuroscience, biology, and robotics (Melendez et al., 2021; Cook et al., 2008; Shababo et al., 2013; Liepe et al., 2013; Schultheis et al., 2020). In such settings, each experiment can involve substantial costs related to time, labor, materials, and financial investments, making it imperative to extract as much information as possible from every trial. By explicitly modeling uncertainty over latent parameters and quantifying the informativeness of potential measurements, Bayesian experimental design (Lind- 

> 1AMLab, UvA-Bosch Delta Lab, University of Amsterdam, Netherlands. 2Department of Electrical Engineering and Automation, Aalto University, Finland. 3School of Mathematics, University of Edinburgh, United Kingdom. 4Department of Statistics, University of Warwick, United Kingdom.. Correspondence to: Hany Abdulsamad _<_ h.abdulsamad@uva.nl _>_ , Sahel Iqbal _<_ sahel.iqbal@aalto.fi _>_ , Christian A. Naesseth _<_ c.a.naesseth@uva.nl _>_ , Takuo Matsubara _<_ Takuo.Matsubara@ed.ac.uk _>_ , Adrien Corenflos _<_ adrien.corenflos@warwick.ac.uk _>_ . 

ley, 1956; Chaloner & Verdinelli, 1995) offers a principled framework for selecting experiments that are maximally informative. To do so, it ties decision-making and Bayesian inference into a single objective aiming to find a design minimizing posterior distribution _uncertainty_ , measured in terms of entropy and averaged over the marginal distribution of prospective measurements. This information-theoretic approach enables efficient allocation of experimental effort, reducing both cost and risk while accelerating scientific discovery, particularly where simulators enable large-scale evaluation of designs prior to deployment. 

However, accurate simulators remain the exception rather than the rule, even as modeling capabilities continue to improve. Mechanical, chemical, and biological systems often exhibit complex and only partially understood interactions that cannot be faithfully captured by idealized assumptions (Rondelez, 2012; van Sluijs et al., 2024). Designs optimized under misspecified simulators may therefore lead to ineffective experiments or, in extreme cases, counterproductive outcomes. Hence, when the model is misspecified, robustness is paramount both in the posterior update and in the data generation governed by the marginal distribution. The decision-making literature has a rich history of addressing misspecification in the data-generating process (Whittle, 1990; Petersen et al., 2002), while the Bayesian inference literature has developed extensive methodology for better posterior updates under likelihood misspecification (Grunwald¨ , 2012; Bissiri et al., 2016; Ghosh & Basu, 2016; Holmes & Walker, 2017; Grunwald & van Ommen¨ , 2017). The central challenge in robust Bayesian experimental design is to unify these perspectives in a single framework that treats robustness in data generation and inference jointly, capturing their interaction rather than addressing them in isolation. 

This problem has attracted increasing attention in recent work. One popular approach to robustify Bayesian inference is to replace the log-likelihood with alternative utility functions or proper scoring rules (Gneiting & Raftery, 2007), yielding what are known as Gibbs posteriors (Zhang, 2006; Bissiri et al., 2016). Recent contributions to robust Bayesian experimental design have adopted this framework, substituting standard posteriors appearing in the expected information gain objective with Gibbs posteriors. Additionally, these methods modify the generative component, either by introducing user-specified distributions (Overstall et al., 

_Preprint. March 17, 2026._ 

1 

**Maximin Robust Bayesian Experimental Design** 

2025) or by constructing simulators implicitly defined by the chosen scoring rule (Barlas et al., 2025). While these approaches offer practical mechanisms for robustifying experimental design, their _ad hoc_ formulations lack a coherent optimization perspective of misspecification. 

In contrast, we propose a principled framework for robust Bayesian experimental design under model misspecification, formulated as a max–min statistical decision problem (Berger, 1985). Misspecification is handled through the lens of distributionally robust optimization (Kuhn et al., 2025) by considering worst-case perturbations of the datagenerating process within a Kullback–Leibler neighborhood centered at a nominal model representing the experimenter’s best approximation to reality. This formulation yields a tractable solution in the form of a Renyi’s mutual informa-´ tion, specifically Sibson’s _α_ -mutual information (Sibson, 1969; Verdu´, 2015; Esposito et al., 2022), which we interpret as a robust expected information gain. However, this quantity must typically be estimated using nested Monte Carlo estimators, which yield biased and stochastic evaluations and thereby undermine the applicability of standard deterministic optimization methods. We therefore adopt a PAC-Bayes approach (McAllester, 1998) that optimizes randomized design policies and provide high-probability guarantees on the true robust expected information gain. 

The remainder of this article is organized as follows. Section 2 reviews Bayesian experimental design. Section 3 formulates robust experimental design as a max–min decision problem and introduces a robust expected information gain based on Sibson’s _α_ -mutual information. Section 4 derives a nested Monte Carlo estimator for our problem and studies its bias and concentration behavior. Section 5 establishes a PAC-Bayes framework for robust design optimization under estimator uncertainty. Section 6 discusses related work, and Section 7 presents numerical evaluations. Finally, all proofs and technical assumptions for presented results are deferred to the supplementary material. 

## **2.1. Expected Information Gain** 

While a variety of expected information criteria have been proposed for defining optimal experimental designs (Huan et al., 2024), the expected information gain (EIG; Lindley, 1956), measuring the mutual information between _θ_ and _x_ , has become the most widely adopted objective in Bayesian experimental design (BED; Rainforth et al., 2024). 

**Definition 1** (Expected information gain) **.** _The expected information gain of a design ξ, defined as the mutual information between the parameters θ and outcomes x, admits several equivalent representations:_ 


![](data/pdf_cache/images/2603.14094.pdf-0002-07.png)


_where_ H _denotes Shannon’s differential entropy and_ DKL _the Kullback–Leibler divergence._ 

Although Shannon’s mutual information is symmetric, so that _I_ ( _θ_ ; _x_ ) _≡ I_ ( _x_ ; _θ_ ), the two orderings admit distinct interpretations. The ordering _I_ ( _θ_ ; _x_ ), represented by (1b), reflects the inferential perspective, emphasizing the expected reduction in uncertainty about the latent parameters _θ_ gained by observing data _x_ . In contrast, the ordering _I_ ( _x_ ; _θ_ ), as expressed in (1c), admits a predictive interpretation, quantifying the extent to which knowledge of _θ_ explains the variability of the outcomes _x_ . While these viewpoints coincide numerically for Shannon’s mutual information, the distinction becomes important when considering general information measures for which symmetry need not hold. 

Given this definition, the goal of Bayesian experimental design is therefore to select the designs _ξ[⋆]_ that maximize the expected information gain: _ξ[⋆]_ = arg max _ξ∈_ Ξ _I_ ( _ξ_ ). 

## **2.2. Variational Mutual Information** 

## **2. Background** 

Let Θ, Ξ and _X_ denote the sets of parameters, designs, and measurements of an experiment, respectively. We write _P_ ( _S_ ) for the set of all probability densities defined on a set _S_ . In Bayesian experimental design, an experimenter selects a design _ξ ∈_ Ξ with the objective of inferring latent parameters _θ ∈_ Θ from observed measurements _x ∈X_ . The experimenter begins with a prior belief _p_ ( _θ_ ) over the parameters and assumes a conditional likelihood function _p_ ( _x | θ, ξ_ ), which specifies how the design _ξ_ relates the latent parameter _θ_ to the observable outcome _x_ . 

The expected information gain, expressed as the mutual information between the parameters _θ_ and measurements _x_ quantifies the minimal information loss incurred by assuming that _θ_ and _x_ are independent when they are in fact not. Equivalently, it measures the irreducible penalty for approximating the true joint _p_ ( _θ, x | ξ_ ) by a surrogate _µ_ ( _θ_ ) _ν_ ( _x | ξ_ ). This perspective implies a variational characterization of mutual information as the minimum expected divergence between the true joint distribution _p_ ( _θ, x | ξ_ ) and an any factorized approximation, as formalized by Verd´u (2015). 

**Lemma 1** (Shannon’s variational mutual information, Verdu´, 2015) **.** _Shannon’s mutual information between θ and x given ξ is the minimal value of the Kullback–Leibler divergence between the true joint distribution and the product of_ 

2 

**Maximin Robust Bayesian Experimental Design** 

_variational marginals:_ 


![](data/pdf_cache/images/2603.14094.pdf-0003-02.png)


_The infimum is attained when the variational marginals coincide with the true marginals, so that µ[⋆]_ ( _θ_ ) = _p_ ( _θ_ ) _and ν[⋆]_ ( _x | ξ_ ) = _p_ ( _x | ξ_ ) _. At this optimum, we obtain:_ 


![](data/pdf_cache/images/2603.14094.pdf-0003-04.png)


This variational formulation allows Verdu´ (2015) to extend the classical mutual information by replacing the Kullback– Leibler divergence with a broader class of divergences. We adopt this viewpoint as the foundation for developing robust information measures in the following sections. 

## **2.3. Stochastic Design Policies** 

The standard formulation of experimental design treats the expected information gain as a function of deterministic designs _ξ ∈_ Ξ, defining the optimal design as _ξ[⋆]_ = arg max _ξ∈_ Ξ _I_ ( _ξ_ ). This approach is adequate provided an exact and deterministic oracle of the objective is available. However, the expected information gain is often intractable and must be approximated by nested Monte Carlo estimators (Rainforth et al., 2018), yielding _biased_ and _noisy_ oracles. To address this challenge, we turn to a PAC-Bayes framework, which provides high-probability guarantees on the estimation error but requires modeling designs as random variables (Flynn et al., 2023; Alquier, 2024). 

Rather than committing to a single design _ξ_ , we consider a setting where the experimenter specifies a probability distribution over the design space, denoted by _π ∈_ Π, which we refer to as a stochastic _policy_ . Concretely, given a generative process _p_ ( _θ, x, ξ_ ) = _p_ ( _θ_ ) _p_ ( _x | θ, ξ_ ) _π_ ( _ξ_ ), the expected information gain associated with a policy _π_ is defined as the _conditional_ mutual information between _x_ and _θ_ given _ξ_ : 


![](data/pdf_cache/images/2603.14094.pdf-0003-09.png)


The optimal experimental design problem is thus reframed as _π[⋆]_ = arg max _π∈_ Π _I_ ( _π_ ). Beyond satisfying a requirement of PAC-Bayes techniques, this relaxation allows us to leverage the rich literature of stochastic policy search methods. Particularly, it enables direct application of informationgeometric optimization techniques, which exploit the curvature of the policy manifold to ensure efficient learning (Amari, 1998). Related algorithmic templates appear in modern policy optimization methods (Peters et al., 2010; Haarnoja et al., 2018), which have demonstrated strong empirical performance in amortizing sequential Bayesian experimental design (Blau et al., 2022; Iqbal et al., 2024). 

## **3. Robust Experimental Design** 

When the measurements encountered at deployment are indeed generated from the assumed conditional likelihood _p_ ( _x | θ[⋆] , ξ_ ) for some _θ[⋆] ∈_ Θ, Bernardo (1979) provides a decision-theoretic justification for the expected information gain. In this well-specified regime, the EIG faithfully reflects the anticipated value of an experiment. 

However, in many applications the likelihood is only a modeling surrogate and may differ substantially from the true data-generating process. Such discrepancies are a wellknown source of systematic error in statistical inference under model misspecification (Grunwald¨ & van Ommen, 2017). The expected information gain is particularly fragile because of its nested dependence on the likelihood: it determines both the posterior _p_ ( _θ | x, ξ_ ) _∝ p_ ( _θ_ ) _p_ ( _x | θ, ξ_ ) and the marginal _p_ ( _x | ξ_ ) = � _p_ ( _x | θ, ξ_ ) _p_ ( _θ_ ) d _θ_ that defines the outer expectation. When the likelihood is misspecified, these quantities do not correspond to the true posterior of _θ_ or the true sampling law for _x_ given a design _ξ_ respectively. As a result, _I_ ( _ξ_ ) may be an unreliable utility, favoring designs that appear highly informative under the assumed model but fail to deliver the anticipated information gain when evaluated against the true data-generating process. 

## **3.1. Maximin Experimental Design** 

To treat this issue systematically, we cast experimental design under misspecification as a two-player zero-sum game between the experimenter and _nature_ (von Neumann & Morgenstern, 1944; Grunwald¨ & Dawid, 2004). The experimenter commits to a policy _π ∈_ Π, and nature counteracts by choosing an adversarial data-generating process _q_ : Ξ _→P_ (Θ _× X_ ) from an admissible set _Q_ . For a fixed design _ξ_ and a data-generating process _q_ , the utility of the experimenter is the mutual information between _θ_ and _x_ : 


![](data/pdf_cache/images/2603.14094.pdf-0003-16.png)



![](data/pdf_cache/images/2603.14094.pdf-0003-17.png)


We impose that _q_ ( _θ_ ) is independent of the design _ξ_ reflecting the assumption that the prior over _θ_ is not affected by experimental choices. Because the experimenter randomizes their designs, performance is evaluated under the induced distribution _ξ ∼ π_ , leading to the payoff functional _V_ ( _π, q_ ) := E _π_ � _U_ ( _ξ, q_ )�. We assume the experimenter knows the uncertainty set _Q_ but not nature’s realized model _q ∈Q_ , while nature observes the policy _π ∈_ Π but not the experimenter’s realized design draw _ξ_ . The experimenter seeking robustness against nature’s choice must then solve the maximin problem (Wald, 1950; Berger, 1985) _V[⋆]_ := _π_ sup _∈_ Π _q_ inf _∈Q[V]_[ (] _[π, q]_[)] _[.]_ 

When the ambiguity set _Q_ is unrestricted, the resulting worst-case formulation is uninformative, since nature can 

3 

**Maximin Robust Bayesian Experimental Design** 

trivially drive the mutual information to zero by enforcing independence between _θ_ and _x_ . A meaningful notion of robustness therefore requires constraining nature’s flexibility by specifying how far nature’s choice _q_ ( _· | ξ_ ) may deviate from a nominal reference model _p_ ( _· | ξ_ ). In our setting, where the experimenter commits to a stochastic policy, it is natural to consider an adversary who is constrained by an average misspecification budget over the support of _π_ . 

Following the framework of distributionally robust optimization (Kuhn et al., 2025), we formalize this restriction by introducing a Kullback–Leibler ambiguity set _Qρ_ . 

**Definition 2** (Ambiguity set) **.** _Let ρ >_ 0 _be a misspecification budget. The ambiguity set Qρ_ ( _π_ ) _consists of all distributions q_ : Ξ _→P_ (Θ _× X_ ) _that lie within an average Kullback–Leibler neighborhood of p_ ( _θ, x | ξ_ ) _:_ 


![](data/pdf_cache/images/2603.14094.pdf-0004-04.png)


_where p_ ( _· | ξ_ ) _denotes the experimenter’s nominal model. Small values of ρ reflect strong confidence in p_ ( _· | ξ_ ) _, while larger values permit greater adversarial perturbations._ 

This global constraint implies that nature can strategically allocate its budget, attacking informative regions of the design space more aggressively while ignoring uninformative ones, provided the average distortion remains bounded. 

In the following lemma, we study the inner minimization problem inf _q∈Qρ V_ ( _π, q_ ), which defines the worst-case utility from the experimenter’s perspective. As both the expected utility and the constraint are linear in _π_ , the global minimization decomposes into independent problems for every design _ξ ∈_ Ξ. 

**Lemma 2** (Minimization decomposition) **.** _The worst-case criterion_ inf _q∈Qρ V_ ( _π, q_ ) _reduces to a dual form:_ 


![](data/pdf_cache/images/2603.14094.pdf-0004-09.png)



![](data/pdf_cache/images/2603.14094.pdf-0004-10.png)


## **3.2. Robust Expected Information Gain** 

Solving the minimization defined by _Jβ_ ( _ξ_ ) leads to the Lapidoth–Pfister mutual information (Lapidoth & Pfister, 2019). However, this objective generally lacks a closedform expression, limiting its applicability. More importantly, it is poorly aligned with experimental design, as it allows nature to freely manipulate the marginal _q_ ( _θ_ ), thereby overriding the experimenter’s prior _p_ ( _θ_ ). As a result, an adversary can expend their budget driving _q_ ( _θ_ ) far from _p_ ( _θ_ ), forcing the experimenter to neglect likelihood misspecification in favor of robustifying against scenarios that lie entirely outside their prior beliefs. 

Instead, we replace the utility _U_ ( _ξ, q_ ) in (2) with its upper envelope _S_ ( _ξ, q_ ), defined by 


![](data/pdf_cache/images/2603.14094.pdf-0004-14.png)


This utility penalizes deviations from the experimenter’s prior and leads to the following worst-case objective: 


![](data/pdf_cache/images/2603.14094.pdf-0004-16.png)


with Γ _β_ ( _ξ_ ) _≥Jβ_ ( _ξ_ ) for all _ξ ∈_ Ξ. This definition yields a tractable notion of robust expected gain and of the worstcase adversarial generation. 

**Proposition 1** (Robust expected information gain) **.** _For any design ξ ∈_ Ξ _and regularization parameter β >_ 0 _, let α_ := _β/_ (1 + _β_ ) _∈_ (0 _,_ 1) _. Then the robust expected information gain_ Γ _β_ ( _ξ_ ) _admits the closed-form expression:_ Γ _β_ ( _ξ_ ) = inf _ν_[D] _[α]_ � _p_ ( _θ, x | ξ_ ) �� _p_ ( _θ_ ) _ν_ ( _x | ξ_ )� = D _α_ � _p_ ( _θ, x | ξ_ ) �� _p_ ( _θ_ ) _pα_ ( _x | ξ_ )� := _IαS_[(] _[θ]_[;] _[ x]_[)(] _[ξ]_[)] _[,] where_ D _α denotes Renyi’s´ divergence of order α and the tilted marginal pα_ ( _· | ξ_ ) _is given by:_ 


![](data/pdf_cache/images/2603.14094.pdf-0004-19.png)


The quantity _Iα[S]_[(] _[θ]_[;] _[ x]_[)][is][Sibson’s] _[α]_[-mutual][informa-] tion (Sibson, 1969; Verdu´, 2015; Esposito et al., 2022; 2024), which we interpret as a _robust expected information gain_ . Crucially, the order parameter _α_ emerges not as a heuristic but in a principled manner as the dual variable associated with the radius _ρ_ of the ambiguity set, serving as an implicit measure of the experimenter’s confidence in _p_ ( _θ, x | ξ_ ). **Corollary 1** (Worst-case generative process) **.** _Let α ∈_ (0 _,_ 1) _be the misspecification order uniquely determined by the ambiguity radius ρ. The worst-case joint distribution q[⋆]_ ( _θ, x | ξ_ ) _that minimizes the objective in Proposition 1 is given by the following geometric mixture:_ 


![](data/pdf_cache/images/2603.14094.pdf-0004-21.png)


_where the α-marginal pα_ ( _x | ξ_ ) _is defined by_ (4) _. Consequently, the worst-case parameter posterior is_ 


![](data/pdf_cache/images/2603.14094.pdf-0004-23.png)


Corollary 1 shows how Sibson’s _α_ -mutual information leads to robustness at the Bayesian inference level. The _α_ -tilted posterior (5) arises as the optimal belief update under the worst-case generative process. Therefore, acting consistently with this adversarial assumption requires the experimenter to update beliefs about _θ_ using this tempered rule rather than the standard Bayesian posterior. By downweighting the misspecified likelihood with _α ∈_ (0 _,_ 1), this 

4 

**Maximin Robust Bayesian Experimental Design** 

result aligns with generalized Bayesian inference techniques for handling model misspecification (see, e.g., Grunwald¨ , 2012; Watson & Holmes, 2016; Grunwald & van Ommen¨ , 2017; Knoblauch et al., 2022, and references therein). 

Meanwhile, robustness at the design level is governed by the monotonicity of Sibson’s _α_ -mutual information with respect to _α_ (Esposito et al., 2024). As _α →_ 1, the active set contracts and the adversarial influence of nature vanishes, and _Iα[S]_[(] _[θ]_[;] _[ x]_[)][ recovers the standard expected information gain in] Definition 1 (Esposito et al., 2024). In this limit, optimal designs coincide with those obtained under the nominal model. As _α_ decreases, the maximum achievable information gain diminishes, reflecting the increasing cost of adversarial attacks. In this regime, _Iα[S]_[(] _[θ]_[;] _[ x]_[)][favors][designs][that][yield] consistent, though potentially smaller, information gains across all adversarial attacks. In the limit _α →_ 0, nature exerts maximal influence, nullifying any gain. 

**Proposition 2** (Uninformative design) **.** _Under Assumption 1, as α →_ 0 _, the robust expected information gain converges to_ 0 _:_ 


![](data/pdf_cache/images/2603.14094.pdf-0005-04.png)


## **3.3. Risk-Sensitive Interpretation** 

Another interpretation of the robust measure _Iα[S]_[(] _[θ]_[;] _[ x]_[)(] _[ξ]_[)] from Proposition 1 is given by the following decomposition. **Proposition 3** (Robust conditional information gain) **.** _The robust expected information gain Iα[S]_[(] _[θ]_[;] _[ x]_[)(] _[ξ]_[)] _[ decomposes] into a risk-sensitive exponential average of conditional R´enyi divergences between prior and posterior:_ 


![](data/pdf_cache/images/2603.14094.pdf-0005-07.png)


_where Gα_ ( _x, ξ_ ) _represents the robust information gain conditional on a specific outcome-design pair_ ( _x, ξ_ ) _:_ 


![](data/pdf_cache/images/2603.14094.pdf-0005-09.png)


This representation directly mirrors the interpretation of Shannon’s mutual information, defined in (1a), as an expected divergence between prior and posterior in the wellspecified setting. However, it identifies the conditional utility _Gα_ ( _x, ξ_ ) as the Renyi divergence between the nominal´ posterior and the prior, while the overall robust expected information gain _Iα[S]_[(] _[θ]_[;] _[ x]_[)(] _[ξ]_[)][ aggregates these conditional] gains through a risk-sensitive exponential average. 

## **4. Nested Monte Carlo Estimator** 

The robust expected information gain _Iα[S]_[:=] _[ I] α[S]_[(] _[θ]_[;] _[ x]_[)][ only] has closed form solutions in special cases. We propose to 

use a simple nested Monte Carlo estimator to estimate it in the general case. We use the following decomposition of Sibson’s _α_ -mutual information for estimation. 

**Corollary 2** (Nested representation of _Iα[S]_[)] **[.]** _[The robust ex-] pected information gain Iα[S]_[(] _[ξ]_[)] _[ can be expressed in terms of] nested expectations over nonlinear maps:_ 


![](data/pdf_cache/images/2603.14094.pdf-0005-15.png)


To simplify the exposition, we define the outer logarithmic transformation _f_ ( _y_ ) := _α/_ ( _α −_ 1) log( _y_ ) and the inner power function _h_ ( _u_ ) := _u_[1] _[/α]_ . Using this notation, the robust objective can be written compactly as _Iα[S]_[(] _[ξ]_[) =] _[ f]_[(] _[g]_[(] _[ξ]_[))][,] where _g_ ( _ξ_ ) represents the nested expectation: 


![](data/pdf_cache/images/2603.14094.pdf-0005-17.png)


**Definition 3** (Nested Monte Carlo estimator _I_[˜] _α[S]_[)] **[.]** _[For][a] design ξ and misspecification order α, the empirical estimator I_[˜] _α[S]_[(] _[ξ]_[)][:=] _[f]_[(˜] _[g]_[(] _[ξ]_[))] _[is][constructed][using][a][nested] Monte Carlo scheme. Let {_ ( _θ_[(] _[i]_[)] _, x_[(] _[i]_[)] ) _}[N] i_ =1 _[be a set of sam-] ples drawn from the joint distribution, and {θ_[(] _[i,j]_[)] _}[M] j_ =1 _[an] independent set of samples drawn from the prior. We define:_ 


![](data/pdf_cache/images/2603.14094.pdf-0005-19.png)


_When the exact density ratio is intractable, we substitute it with the contrastive estimator w_ ˜ _using K auxiliary samples:_ 


![](data/pdf_cache/images/2603.14094.pdf-0005-21.png)


Appendix C provides a numerically stable method for computing the estimator. Because the estimator applies the nonlinear functions to empirical averages rather than exact expectations, Jensen’s inequality implies that it is biased for any finite sample sizes _N_ and _M_ . Nonetheless, the analysis of Rainforth et al. (2018) establishes that it remains consistent and its mean squared error decays as _O_ (1 _/N_ + 1 _/M_ ), when _w_ is available in closed form. 

Next, we provide explicit bounds for its bias under Assumption 2, which defines regularity constants _Lf_ , _Lh_ , _Ch_ , _σh_ , and _σw_ for the functions _f_ , _h_ and _w_ . 

**Proposition 4** (Bias bound for _I_[˜] _α[S]_[)] **[.]** _[Let][I]_[˜] _α[S]_[(] _[ξ]_[)] _[ be the esti-] mator of Iα[S]_[(] _[ξ]_[)] _[ given by Definition][ 3][.][Under Assumption][ 2][,] for any design ξ ∈_ Ξ _, the bias of I_[˜] _α[S]_[(] _[ξ]_[)] _[ is bounded by:]_ 


![](data/pdf_cache/images/2603.14094.pdf-0005-25.png)


5 

**Maximin Robust Bayesian Experimental Design** 

## **5. PAC-Bayesian Design Policies** 

In the previous section, we introduced a nested Monte Carlo estimator _I_[˜] _α[S]_[(] _[ξ]_[)][for][the][robust][expected][information][gain] _Iα[S]_[(] _[ξ]_[)][.][However,][this][estimator][is][a][biased][and][noisy][or-] acle, introducing errors that can mislead design selection if optimized naively. To address this, we adopt stochastic design policy and control the estimator error through a PACBayesian approach. In Appendix D, we provide discussion on classical PAC analysis and the PAC-Bayesian approach. 

We view design selection as a PAC-Bayes continuous bandit problem (Flynn et al., 2023), where the designs _ξ_ are arms and the true rewards are determined by _Iα[S]_[, observed] only through the noisy surrogate _I_[˜] _α[S]_[.][The][PAC-Bayesian] formulation optimizes a high-probability lower bound on the true robust objective by penalizing the divergence to a prior policy _π_ 0, thereby balancing empirical performance against estimator uncertainty (Alquier, 2024). 

To establish the PAC-Bayesian guarantee, we leverage results of prior sections to derive a probability bound on the bias of the robust expected information gain estimator. 

**Proposition 5** (Uniform convergence of _I_[˜] _α[S]_[)] **[.]** _[Let][I]_[˜] _α[S]_[(] _[ξ]_[)] _[ be] the estimator of Iα[S]_[(] _[ξ]_[)] _[ from Definition][ 3][ .][Under Assump-] tion 2, for any tolerance t >_ 0 _, and for a sufficiently large inner sample size M ≥_ 4 _L_[2] _f[L] h_[2] _[σ] w_[2] _[/t]_[2] _[, the probability that] the estimator deviates from the oracle by more than t decays exponentially with the outer sample size N :_ 


![](data/pdf_cache/images/2603.14094.pdf-0006-06.png)


Proposition 5 effectively states that the absolute error of our naive estimator _I_[˜] _α[S]_[behaves like a sub-Gaussian random] variable _if_ we pay the cost _M_ to make it so. Given this concentration property, we can now establish a PAC-Bayes lower bound for the robust expected information gain. **Proposition 6** (PAC-Bayes lower bound for _Iα[S]_[)] **[.]** _[Let] π_ 0 _∈_ Π _be a prior design policy, δ ∈_ (0 _,_ 1) _a confidence level, and λ >_ 0 _a precision parameter. Provided M ≥_ 2 _NL_[2] _h[σ] w_[2] _[/]_[(] _[C] h_[2][log(2] _[/δ]_[))] _[,][then][with][probability][at] least_ 1 _− δ, this bound holds for all π ∈_ Π _simultaneously:_ 


![](data/pdf_cache/images/2603.14094.pdf-0006-08.png)


Proposition 6 yields a high-probability lower bound on the truesurrogate _robust_ E objective _π_ � _I_ ˜ _αS_[(] _[ξ]_[)] � Eand the penalty _π_ � _Iα[S]_[(] _[ξ]_[)] � expressed in terms of the DKL[ _π ∥ π_ 0]. Since the remaining terms in the bound are independent of _π_ , maximizing this lower bound over Π reduces to the following 

variational optimization problem: 


![](data/pdf_cache/images/2603.14094.pdf-0006-11.png)


whose maximizer is given by a Gibbs policy (Alquier, 2024): 


![](data/pdf_cache/images/2603.14094.pdf-0006-13.png)


This objective can be optimized using stochastic policy search methods, including natural gradient and mirror descent algorithms (Amari, 1998; Kakade, 2001; Beck & Teboulle, 2003; Peters et al., 2010). 

## **6. Related Work** 

The two works most closely related to ours methodologically are Go & Isaac (2022) and Waite & Woods (2022). Go & Isaac (2022) also adopt a distributionally robust optimization framework, but focus on prior misspecification, leading to a risk-sensitive objective based on log-exponential averages of Kullback–Leibler divergences rather than a Renyi-´ type divergence. By contrast, our maximin formulation naturally recovers Sibson’s _α_ -mutual information. Waite & Woods (2022) study maximin experimental design from a _frequentist_ perspective and consider stochastic policies. However, the absence of prior beliefs over _θ_ leads to a different mechanism for constructing robust designs, and their theoretical analysis is confined to linear models. 

Two recent works have applied Gibbs posteriors in the context of Bayesian experimental design: Overstall et al. (2025) and Barlas et al. (2025). In both cases, the Gibbs posterior is introduced as an _ad hoc_ device to robustify the inference procedure given a design and a measured outcome. In contrast, in our framework the tilted posterior (5) emerges naturally from the maximin robustness principle as the experimenter’s robust belief update rule. This construction leads to a unified formulation in which misspecification is addressed jointly at the level of posterior inference and the data-generating process, in contrast to Overstall & McGree (2022); Overstall et al. (2025), where these aspects are addressed separately. 

A related line of work develops alternative utility functions that incorporate information from the _true, but unknown_ data-generating process. Catanach & Das (2023) introduce the expected generalized information gain, replacing the KL divergence in (1a) with a discrepancy measure defined under the true process. Since this quantity is not directly computable, their approach requires specifying a model class containing the true process and evaluating the sensitivity of the utility with respect to parameters indexing this class. Similarly, Tang et al. (2025) augment the EIG with a penalty on covariate shifts between the training data collected using optimized designs and a reference test set. Therefore, the proposed acquisition function is constrained by the availability of such test data. 

6 

**Maximin Robust Bayesian Experimental Design** 

Finally, some complementary approaches address misspecification through increased model flexibility, for example by augmenting the model with expressive components such as Gaussian processes (Feng, 2015; Forster et al., 2025). 

## **7. Numerical Evaluation** 

Our evaluation will focus on two main aspects. First, we highlight the properties of Sibson’s _α_ -mutual information as a criterion for robust experimental design, emphasizing that robustness manifests on the levels of the posterior update and design selection. Second, when the robust EIG is only available through a biased and noisy empirical estimator, we show that naive deterministic design optimizers can yield suboptimal designs, hence validating the need for the PACBayes policy for design optimization. 

To study the properties of Sibson’s _α_ -MI, we focus on two problem settings in which all relevant quantities admit closed-form expressions. This lets us isolate the behavior of Sibson’s _α_ -MI without confounding numerical artifacts. Specifically, we consider a continuous linear regression problem and a discrete A/B testing problem, which allow for exact computation of posterior updates, conditional information gains, and Sibson’s _α_ -MI. Details on computations are provided in Appendices E.1 and E.2. 

1. In linear regression, measurements are real-valued responses _x ∈_ R generated according to the Gaussian 


![](data/pdf_cache/images/2603.14094.pdf-0007-06.png)


where _ξ ∈_ [ _−_ 1 _,_ 1] is the design and the parameters are _θ_ = ( _θ_ 1 _, θ_ 2) _[⊤] ∈_ R[2] , with prior _p_ ( _θ_ ) = N( _θ_ ; _µ_ 0 _,_ Σ0). 

2. In A/B testing, measurements are counts _x_ = ( _xa, xb_ ) _∈{_ 0 _, . . . , na}×{_ 0 _, . . . , nb}_ from a Binomial _p_ ( _x | θ, ξ_ ) =[�] _k_[Bin(] _[x][k]_[;] _[ n][k][, θ][k]_[)] _[,] k ∈{a, b}._ 

The design _ξ_ = _na ∈{_ 0 _, . . . , Nx}_ controls group allocation (with _nb_ = _Nx − na_ ), and the parameters are _θ_ = ( _θa, θb_ ) _[⊤] ∈_ [0 _,_ 1][2] with independent Beta priors _p_ ( _θ_ ) =[�] _k_[Beta(] _[θ][k][∈{][a,b][}]_[;] _[ δ][k][, γ][k]_[)][.] 

**Sibson’s** _α_ **-mutual information.** Here we assume that in 

both settings the true data-generating process is a tilted version of the corresponding nominal model described earlier, as characterized in Corollary 1. 

We compare the _realized_ information gain under nominal and robust formulations. The nominal approach uses the Kullback–Leibler divergence (1a) as a measure, while the robust approach relies on Renyi’s divergence´ (6). Figure 1 displays histograms from 10[4] simulated experiments for the linear regression and A/B testing problems. Crucially, we evaluate each gain metric using its respective optimal 


![](data/pdf_cache/images/2603.14094.pdf-0007-13.png)


**----- Start of picture text -----**<br>
× 10 [3] Linear Regression × 10 [3] A/B Testing<br>4 Nominal<br>2<br>Robust<br>1 2 Sibson MI<br>0 0<br>4 5 6 7 0 2 4 6 8 10<br>Information Gain Information Gain<br>Figure 1. Comparison of realized information gains under nominal<br>and robust formulations for linear regression (left) and A/B test-<br>ing (right). Histograms show the empirical distributions of gains<br>obtained from 10 10 [[4]] simulations using optimal designs. The dashed<br>line indicates the Sibson  α -mutual information benchmark.<br>Linear Regression A/B Testing<br>1<br>0 . 5<br>0<br>0 0 . 5 1 0 0 . 5 1<br>Expected Coverage Expected Coverage<br>Nominal (optimal) Robust (optimal) Nominal (random) Robust (random)<br>Frequency<br>Actual Coverage<br>**----- End of picture text -----**<br>


_Figure 1._ Comparison of realized information gains under nominal and robust formulations for linear regression (left) and A/B testing (right). Histograms show the empirical distributions of gains obtained from 10 10[[4]] simulations using optimal designs. The dashed line indicates the Sibson _α_ -mutual information benchmark. 

_Figure 2._ Comparison of expected and actual coverage for nominal and robust posteriors given optimal and random designs in linear regression (left) and A/B testing (right). Nominal posteriors are overconfident, while robust posteriors are systematically conservative. Optimizing the design amplifies conservativeness further. 

design. The nominal approach appears to yield higher gains, but it is important to remember that this gain reflects a _subjective_ utility that assumes the data-generating process is perfectly known, leading the experimenter to overstate the informativeness of the executed experiments. 

This overconfidence is revealed by the coverage analysis in Figure 2. Coverage measures posterior calibration by comparing expected credible levels to the empirical frequency with which the true parameter falls within the corresponding credible sets. For the _nominal_ Bayesian posterior, coverage curves lie well below the diagonal, indicating systematic overconfidence and undercoverage. In contrast, our _robust_ tilted posterior exhibits a conservative behavior that underpromises but overdelivers. Robustness operates at two levels. At inference, the robust posterior induces a cautious update that prevents over-concentration regardless of the design. At design selection, optimizing Sibson’s _α_ -mutual information reinforces conservativeness by selecting experiments that are less sensitive to model misspecification. 

Finally, Table 1 reports predictive performance measured by the expected log-predictive density on a held-out test set. Although our objective does not directly optimize a predictive measure, designs optimized via Sibson’s _α_ -mutual information consistently outperform random designs, suggesting that the induced conservativeness translates into more reli- 

7 

**Maximin Robust Bayesian Experimental Design** 

_Table 1._ Expected log-predictive density for linear regression and A/B testing comparing robust posteriors under random and optimal designs across varied _α_ values. Mean values over 10[4] trials. 


![](data/pdf_cache/images/2603.14094.pdf-0008-02.png)


**----- Start of picture text -----**<br>
Linear Regression A/B Testing<br>Order  α Random Optimal Random Optimal<br>0.01 − 2 . 624 − 2 . 306 − 29 . 812 − 20 . 314<br>0.05 − 1 . 353 − 0 . 780 − 17 . 673 − 15 . 935<br>0.1 − 0 . 831 − 0 . 185 − 16 . 790 − 16 . 145<br>0.5 − 0 . 085 0 . 635 − 16 . 879 − 17 . 004<br>1.0 − 0 . 376 0 . 341 − 17 . 082 − 17 . 143<br>× 10 [2]<br>6<br>Naive<br>4 PAC-Bayes<br>2<br>0<br>0 0 . 2 0 . 4 0 . 6 0 . 4 0 . 6 0 . 8 1<br>× 10 [2]<br>10<br>5<br>0<br>0 0 . 1 0 . 2 0 . 6 0 . 7 0 . 8 0 . 9 1<br>Objective Regret Design Optimality<br>Frequency<br>Frequency<br>**----- End of picture text -----**<br>


_Figure 3._ Empirical distributions of regret (left) and design optimality (right) across 1024 simulations for a naive optimizer and a PAC-Bayes policy for linear regression (top) an A/B testing (bottom). The naive optimizers exhibit higher regret and variability. Their designs are suboptimal, reflected in smaller design ratios relative to the theoretically optimal design. 

_Table 2._ Regret comparison on a linear regression problem between a naive optimizer and a PAC-Bayes policy for varying sample sizes _N_ , with _M_ = 16. We report the mean regret together with the 10th and 90th percentiles, computed over 256 repetitions. 

|_N_|Naive<br>Mean<br>_P_10<br>_P_90|PAC-Bayes<br>Mean<br>_P_10<br>_P_90|
|---|---|---|
|16|0.238<br>0.133<br>0.350|**0**_._**017**<br>**0**_._**015**<br>**0**_._**021**|
|32|0.215<br>0.121<br>0.325|**0**_._**021**<br>**0**_._**015**<br>**0**_._**032**|
|64|0.192<br>0.111<br>0.291|**0**_._**012**<br>**0**_._**010**<br>**0**_._**014**|
|128|0.174<br>0.097<br>0.266|**0**_._**010**<br>**0**_._**008**<br>**0**_._**011**|
|256|0.153<br>0.088<br>0.232|**0**_._**010**<br>**0**_._**008**<br>**0**_._**011**|



_Table 3._ Relative regret comparison on a linear regression problem between a naive optimizer and a PAC-Bayes policy across varying _α_ values. We report the mean relative regret together with the 10th and 90th percentiles, computed over 256 repetitions. 

|_α_<br>|Naive<br>Mean<br>_P_10<br>_P_90<br><br><br>|PAC-Bayes<br>Mean<br>_P_10<br>_P_90|
|---|---|---|
|0.01<br>0.05<br>01|0.092<br>0.061<br>0.123<br>0.113<br>0.076<br>0.149<br>0113<br>0077<br>0145|**0**_._**020**<br>**0**_._**015**<br>**0**_._**026**<br>**0**_._**024**<br>**0**_._**013**<br>**0**_._**039**<br>**0007**<br>**0005**<br>**0008**|
|.|.<br>.<br>.|_._<br>_._<br>_._|
|0.5|0.101<br>0.064<br>0.136|**0**_._**006**<br>**0**_._**004**<br>**0**_._**008**|
|1.0|0.097<br>0.063<br>0.131|**0**_._**009**<br>**0**_._**006**<br>**0**_._**011**|



Bayes policy. Table 3 confirms that this performance gap holds uniformly across different values of _α_ . For fixed sample sizes _N_ and _M_ , the naive optimizers consistently incurs higher regret than the PAC-Bayes policy, validating the PAC-Bayesian perspective. 

able predictive performance under misspecification. 

**PAC-Bayes policies.** While the preceding evaluation relied on closed-form formulas for computation, this section focuses on optimizing designs using the nested Monte Carlo estimator, thereby foregoing any benefits of analytical tractability. To test design optimization in a higherdimensional setting, we extend the linear regression problem to a 10-dimensional parameter and design space, while A/B testing accommodates _Nx_ = 100 subjects. 

Figure 3 depicts the failure of naive design optimization when the objective is estimated by a noisy, biased oracle. We compare gradient descent for linear regression and exhaustive enumeration for A/B testing against a PAC-Bayes stochastic policy optimized via mirror descent, while fixing _α_ , _λ_ , and the sample sizes _N_ and _M_ . We repeat the naive optimization 1024 times and evaluate realized regret and design optimality relative to the tractable optimum. The histograms show that naive optimizers incur higher and more variable regret, reflecting suboptimal designs, whereas the PAC-Bayes policy concentrates near the optimum and achieves consistently lower regret. 

Finally, we examine the impact of sample complexity in Table 2, which reports the mean regret alongside the 10th and 90th percentiles across varying outer sample sizes _N_ . While the performance of the naive optimizer improves as _N_ increases, it fails to match the performance of the PAC- 

## **8. Discussion** 

In this work, we established a principled framework for robust Bayesian experimental design using the maximin principle of decision making. We proposed Sibson’s _α_ - mutual information as a robust alternative to the standard expected information gain, and showed that, under the maximin formulation, the experimenter’s belief update is an _α_ -tilted posterior, while the conditional information gain corresponds to a Renyi divergence between the posterior and´ prior. To address the intractability of Sibson’s _α_ -MI and the finite-sample errors arising from Monte Carlo estimation, we introduced PAC-Bayesian stochastic policies, and proved a lower bound for the true conditional Sibson’s _α_ -MI. Our results provide a complete characterization of maximin robust Bayesian experimental design under information-theoretic constraints: the worst-case adversarial perturbation, the robust conditional and expected information gain measures, and the tilted posterior belief update all emerge naturally from the maximin principle. 

We identify several limitations that present opportunities for future research. First, while the maximin formulation offers rigorous worst-case guarantees, it can lead to overly conservative designs (Watson & Holmes, 2016). Exploring other methods of robust decision making and Bayesian inference and their applicability to experimental design could 

8 

**Maximin Robust Bayesian Experimental Design** 

complement our work. Second, choosing the right value of the parameter _α_ is currently left up to the experimenter, and it is unreasonable to expect that experimenters always know the extent of model misspecification a priori. Developing adaptive methods to tune _α_ sequentially as the experimenter’s knowledge evolves, similar to those in the generalized Bayes literature (Wu & Martin, 2021), is an interesting direction. Finally, we do not address the practical calibration of the PAC-Bayes precision parameter _λ_ . Investigating the benefits and challenges of optimizing the lower bound with respect to _λ_ merits further study. 

## **Acknowledgements** 

H. Abdulsamad and C.A. Naesseth acknowledge funding from the Bosch Center for Artificial Intelligence (BCAI). 

## **References** 

- Alquier, P. User-friendly introduction to PAC-Bayes bounds. _Foundations and Trends® in Machine Learning_ , 17(2): 174–303, 2024. 

- Amari, S.-I. Natural gradient works efficiently in learning. _Neural Computation_ , 10(2):251–276, 1998. 

- Barlas, Y. Z., Sloman, S. J., and Kaski, S. Robust experimental design via generalised Bayesian inference. _arXiv preprint arXiv:2511.07671_ , 2025. 

- Beck, A. and Teboulle, M. Mirror descent and nonlinear projected subgradient methods for convex optimization. _Operations Research Letters_ , 31(3):167–175, 2003. 

- Berger, J. O. _Statistical Decision Theory and Bayesian Analysis_ . Springer New York, 2nd edition, 1985. 

- Bernardo, J. M. Expected information as expected utility. _The Annals of Statistics_ , 7(3):686–690, 1979. 

- Bissiri, P. G., Holmes, C. C., and Walker, S. G. A general framework for updating belief distributions. _Journal of the Royal Statistical Society Series B: Statistical Methodology_ , 78(5):1103–1130, 2016. 

- Blau, T., Bonilla, E. V., Chades, I., and Dezfouli, A. Optimizing sequential experimental design with deep reinforcement learning. In _International Conference on Machine Learning_ , 2022. 

- Boyd, S. and Vandenberghe, L. _Convex Optimization_ . Cambridge University Press, 2004. 

- Catanach, T. A. and Das, N. Metrics for Bayesian optimal experiment design under model misspecification. In _IEEE Conference on Decision and Control_ , pp. 7707–7714, 2023. 

- Catoni, O. PAC-Bayesian supervised classification: The thermodynamics of statistical learning. _Institute of Mathematical Statistics Lecture Notes - Monograph Series_ , 56: 1–163, 2007. 

- Chaloner, K. and Verdinelli, I. Bayesian experimental design: A review. _Statistical Science_ , 10(3):273–304, 1995. 

- Cook, A. R., Gibson, G. J., and Gilligan, C. A. Optimal observation times in experimental epidemic processes. _Biometrics_ , 64(3):860–868, 2008. 

- Csiszar, I.´ Generalized cutoff rates and Renyi’s information´ measures. _IEEE Transactions on Information Theory_ , 41 (1):26–34, 2002. 

- Donsker, M. D. and Varadhan, S. S. Asymptotic evaluation of certain markov process expectations for large time. _Communications on Pure and Applied Mathematics_ , 28 (1):1–47, 1975. 

- Esposito, A. R., Vandenbroucque, A., and Gastpar, M. On Sibson’s _α_ -mutual information. In _IEEE International Symposium on Information Theory_ , pp. 2904–2909, 2022. 

- Esposito, A. R., Gastpar, M., and Issa, I. Sibson’s _α_ -mutual information and its variational representations. _arXiv preprint arXiv:2405.08352_ , 2024. 

- Feng, C. Optimal Bayesian experimental design in the presence of model error. Master’s thesis, Massachusetts Institute of Technology, 2015. 

- Flynn, H., Reeb, D., Kandemir, M., and Peters, J. PACBayes bounds for bandit problems: A survey and experimental comparison. _IEEE Transactions on Pattern Analysis and Machine Intelligence_ , 45(12):15308–15327, 2023. 

- Forster, A., Ivanova, D. R., and Rainforth, T. Improving robustness to model misspecification in Bayesian experimental design. In _Symposium of Advances of Approximate Bayesian Inference_ , 2025. 

- Ghosh, A. and Basu, A. Robust Bayes estimation using the density power divergence. _Annals of the Institute of Statistical Mathematics_ , 68(2):413–437, 2016. 

- Gneiting, T. and Raftery, A. E. Strictly proper scoring rules, prediction, and estimation. _Journal of the American Statistical Association_ , 102(477):359–378, 2007. 

- Go, J. and Isaac, T. Robust expected information gain for optimal Bayesian experimental design using ambiguity sets. In _Conference on Uncertainty in Artificial Intelligence_ , 2022. 

9 

**Maximin Robust Bayesian Experimental Design** 

- Grunwald, P.¨ The safe Bayesian: Learning the learning rate via the mixability gap. In _International Conference on Algorithmic Learning Theory_ , 2012. 

- Grunwald, P. and van Ommen, T.¨ Inconsistency of Bayesian inference for misspecified linear models, and a proposal for repairing it. _Bayesian Analysis_ , 12(4):1069–1103, 2017. 

- Grunwald, P. D. and Dawid, A. P.¨ Game theory, maximum entropy, minimum discrepancy and robust Bayesian decision theory. _The Annals of Statistics_ , 32(4):1367–1433, 2004. 

- Haarnoja, T., Zhou, A., Hartikainen, K., Tucker, G., Ha, S., Tan, J., Kumar, V., Zhu, H., Gupta, A., Abbeel, P., et al. Soft actor-critic algorithms and applications. _arXiv preprint arXiv:1812.05905_ , 2018. 

- Holmes, C. C. and Walker, S. G. Assigning a value to a power likelihood in a general Bayesian model. _Biometrika_ , 104(2):497–503, 2017. 

- Hu, Y., Chen, X., and He, N. Sample complexity of sample average approximation for conditional stochastic optimization. _SIAM Journal on Optimization_ , 30(3):2103– 2133, 2020. 

- Huan, X., Jagalur, J., and Marzouk, Y. Optimal experimental design: Formulations and computations. _Acta Numerica_ , 33:715–840, 2024. 

- Iqbal, S., Corenflos, A., Sarkk¨ a,¨ S., and Abdulsamad, H. Nesting particle filters for experimental design in dynamical systems. In _International Conference on Machine Learning_ , 2024. 

- Kakade, S. M. A natural policy gradient. _Advances in neural information processing systems_ , 14, 2001. 

- Knoblauch, J., Jewson, J., and Damoulas, T. An optimization-centric view on Bayes’ rule: Reviewing and generalizing variational inference. _Journal of Machine Learning Research_ , 23(132):1–109, 2022. 

- Kuhn, D., Shafiee, S., and Wiesemann, W. Distributionally robust optimization. _Acta Numerica_ , 34:579–804, 2025. 

- Lapidoth, A. and Pfister, C. Two measures of dependence. _Entropy_ , 21(8):778, 2019. 

- Liepe, J., Filippi, S., Komorowski, M., and Stumpf, M. P. Maximizing the information content of experiments in systems biology. _PLoS Computational Biology_ , 9(1), 2013. 

- Lindley, D. V. On a measure of the information provided by an experiment. _The Annals of Mathematical Statistics_ , 27 (4):986–1005, 1956. 

- McAllester, D. A. Some PAC-Bayesian theorems. In _Conference on Computational Learning Theory_ , pp. 230–234, 1998. 

- Melendez, J., Furnstahl, R., Grießhammer, H., McGovern, J., Phillips, D., and Pratola, M. Designing optimal experiments: An application to proton Compton scattering. _The European Physical Journal A_ , 57(3):81, 2021. 

- Overstall, A. and McGree, J. Bayesian decision-theoretic design of experiments under an alternative model. _Bayesian Analysis_ , 17(4):1021–1041, 2022. 

- Overstall, A. M., Holloway-Brown, J., and McGree, J. M. Gibbs optimal design of experiments. _arXiv preprint arXiv:2310.17440_ , 2025. 

- Peters, J., Mulling, K., and Altun, Y. Relative entropy policy search. In _AAAI Conference on Artificial Intelligence_ , pp. 1607–1612, 2010. 

- Petersen, I. R., James, M. R., and Dupuis, P. Minimax optimal control of stochastic uncertain systems with relative entropy constraints. _IEEE Transactions on Automatic Control_ , 45(3):398–412, 2002. 

- Rainforth, T., Cornish, R., Yang, H., Warrington, A., and Wood, F. On nesting Monte Carlo estimators. In _International Conference on Machine Learning_ , volume 80, pp. 4267–4276, 2018. 

- Rainforth, T., Foster, A., Ivanova, D. R., and Bickford Smith, F. Modern Bayesian experimental design. _Statistical Science_ , 39(1):100–114, 2024. 

- Rondelez, Y. Competition for catalytic resources alters biological network dynamics. _Physical Review Letters_ , 108(1):018102, 2012. 

Schultheis, M., Belousov, B., Abdulsamad, H., and Peters, J. Receding horizon curiosity. In _Conference on Robot Learning_ , pp. 1278–1288. PMLR, 2020. 

- Shababo, B., Paige, B., Pakman, A., and Paninski, L. Bayesian inference and online experimental design for mapping neural microcircuits. In _International Conference on Neural Information Processing Systems_ , 2013. 

- Sibson, R. Information radius. _Zeitschrift fur Wahrschein-¨ lichkeitstheorie und verwandte Gebiete_ , 14(2):149–160, 1969. 

- Tang, R., Sloman, S. J., and Kaski, S. Generalization analysis for Bayesian optimal experiment design under model misspecification. _arXiv preprint arXiv:2506.07805_ , 2025. 

- van Sluijs, B., Zhou, T., Helwig, B., Baltussen, M. G., Nelissen, F. H., Heus, H. A., and Huck, W. T. Iterative design of training data to control intricate enzymatic reaction networks. _Nature Communications_ , 15(1):1602, 2024. 

10 

**Maximin Robust Bayesian Experimental Design** 

- Verdu, S.´ _α_ -mutual information. In _2015 Information Theory and Applications Workshop (ITA)_ , pp. 1–6. IEEE, 2015. 

- Vershynin, R. _High-Dimensional Probability: An Introduction with Applications in Data Science_ , volume 47. Cambridge university press, 2018. 

- von Neumann, J. and Morgenstern, O. _Theory of Games and Economic Behavior_ . Princeton University Press, 1944. 

- Wainwright, M. J. _High-Dimensional Statistics: A NonAsymptotic Viewpoint_ . Cambridge University Press, 2019. 

- Waite, T. W. and Woods, D. C. Minimax efficient random experimental design strategies with application to modelrobust design for prediction. _Journal of the American Statistical Association_ , 117(539):1452–1465, 2022. 

- Wald, A. _Statistical Decision Functions_ . Wiley, 1950. 

- Watson, J. and Holmes, C. Approximate models and robust decisions. _Statistical Science_ , 31(4):465–489, 2016. 

- Whittle, P. _Risk-Sensitive Optimal Control_ . Wiley, 1990. 

- Wu, P.-S. and Martin, R. Calibrating generalized predictive distributions. _arXiv preprint arXiv:2107.01688_ , 2021. 

- Zhang, T. From _ϵ_ -entropy to KL-entropy: Analysis of minimum information complexity density estimation. _The Annals of Statistics_ , 34(5):2180–2210, 2006. 

11 

**Maximin Robust Bayesian Experimental Design** 

## **A. Organization of the Appendix** 

The Appendix is organized as follows. In Appendix B, we provide proofs for the various lemmas and propositions introduced in the paper. Appendix C provides details on estimating Sibson’s _α_ -MI with a nested Monte Carlo estimator, and Appendix D compares PAC-Bayesian policies to deterministic ones. Appendix E provides details for the numerical evaluations presented in Section 7. Finally, Appendix F discusses different definitions for _α_ -mutual information and their interpretations as adversarial games with differing constraints. 

## **B. Proofs** 

## **B.1. Proof of Lemma 1** 

We decompose the Kullback–Leibler divergence as follows: 


![](data/pdf_cache/images/2603.14094.pdf-0012-06.png)


The second and third terms are nonnegative and equal zero if and only if _µ_ ( _θ_ ) = _p_ ( _θ_ ) and _ν_ ( _x | ξ_ ) = _p_ ( _x | ξ_ ), respectively. Therefore the infimum is achieved at _µ[⋆]_ ( _θ_ ) = _p_ ( _θ_ ) and _ν[⋆]_ ( _x | ξ_ ) = _p_ ( _x | ξ_ ), and the minimum value is given by Shannon’s mutual information: 


![](data/pdf_cache/images/2603.14094.pdf-0012-08.png)


## **B.2. Proof of Lemma 2** 

We consider the worst-case expected utility minimization problem defined by: 


![](data/pdf_cache/images/2603.14094.pdf-0012-11.png)


subject to the Kullback–Leibler constraint averaged under _π_ ( _ξ_ ): 


![](data/pdf_cache/images/2603.14094.pdf-0012-13.png)


Given that both the objective and the constraint are convex in _q_ ( _· | ξ_ ), and under strict feasibility assumptions, strong duality holds (Boyd & Vandenberghe, 2004). Therefore, we can write: 


![](data/pdf_cache/images/2603.14094.pdf-0012-15.png)


where _L_ is the Lagrangian functional given by: 


![](data/pdf_cache/images/2603.14094.pdf-0012-17.png)


As a result, the worst-case expected utility can be written as an expectation over regularized pointwise objectives: 


![](data/pdf_cache/images/2603.14094.pdf-0012-19.png)


where _Jβ_ ( _ξ_ ) is the regularized worst-case utility: 


![](data/pdf_cache/images/2603.14094.pdf-0012-21.png)


12 

**Maximin Robust Bayesian Experimental Design** 

## **B.3. Proof of Proposition 1** 

Starting from the definition of Γ _β_ ( _ξ_ ) for any _β >_ 0: 


![](data/pdf_cache/images/2603.14094.pdf-0013-03.png)


and leveraging the variational form of _S_ ( _ξ, q_ ) as stated in Lemma 1: 

we can write the following minimization problem: 


![](data/pdf_cache/images/2603.14094.pdf-0013-06.png)


with implicit constraints to ensure that _q_ ( _θ, x | ξ_ ) and _ν_ ( _x | ξ_ ) are proper densities. 

The infimum operators commute and we can exchange the order of minimization to inf _ν_ inf _q_ . For any fixed marginal _ν_ , the inner minimization over _q_ is a convex optimization problem with a convex constraint and strong duality holds under strict feasibility assumptions (Boyd & Vandenberghe, 2004). 

To form the associated Lagrangian functional, we introduce the multipliers _η_ and _κ_ associated with the nomralization constraints. The resulting dual problem is: 


![](data/pdf_cache/images/2603.14094.pdf-0013-10.png)


where the Lagrangian functional _G_ is given by: 


![](data/pdf_cache/images/2603.14094.pdf-0013-12.png)


We start by minimizing _G_ with respect to the joint distribution _q_ ( _· | ξ_ ). We take the first variation of _G_ and set it to zero to obtain a stationarity condition: 


![](data/pdf_cache/images/2603.14094.pdf-0013-14.png)


Solving for _q[⋆]_ ( _· | ξ_ ): 


![](data/pdf_cache/images/2603.14094.pdf-0013-16.png)


and accounting for the optimal normalization multiplier _η[⋆]_ , we get the geometric mixture: 


![](data/pdf_cache/images/2603.14094.pdf-0013-18.png)


where _β/_ (1 + _β_ ) interpolates geometrically between the factorized reference and the nominal joint model. Substituting the optimum _q[⋆]_ ( _· | ξ_ ) back into the Lagrangian (7) eliminates the dependence and reduces the functional to depend only on variational marginal _ν_ ( _· | ξ_ ) and the multipliers _β_ and _κ_ : 


![](data/pdf_cache/images/2603.14094.pdf-0013-20.png)



![](data/pdf_cache/images/2603.14094.pdf-0013-21.png)


13 

**Maximin Robust Bayesian Experimental Design** 

where we have introduced a shorthand for the _soft_ marginal likelihood: 


![](data/pdf_cache/images/2603.14094.pdf-0014-02.png)


We now consider the first variation of _G_ with respect to _ν_ ( _· | ξ_ ), yielding the stationarity condition: 


![](data/pdf_cache/images/2603.14094.pdf-0014-04.png)


Similar to _q_ ( _· | ξ_ ), solving for _ν[⋆]_ ( _· | ξ_ ) while accounting for the optimal normalization multiplier _κ[⋆]_ leads to: 


![](data/pdf_cache/images/2603.14094.pdf-0014-06.png)


This distribution is a tilted marginal induced by the constraint. Its dependence on _β_ encodes how aggressively mass is concentrated on high-likelihood regions. Substitute this result back into _G_ to get the dual as a function of _β_ only: 


![](data/pdf_cache/images/2603.14094.pdf-0014-08.png)


where D _ω_ denotes the R´enyi divergence of order _ω_ . Finally, we substitute _α_ = _β/_ (1 + _β_ ) with _α ∈_ (0 _,_ 1): 

_S_ Γ _β_ ( _ξ_ ) = D _α_ � _p_ ( _θ, x | ξ_ ) �� _p_ ( _θ_ ) _pα_ ( _x | ξ_ )� := _Iα_[(] _[θ]_[;] _[ x]_[)(] _[ξ]_[)] _[.]_ 

Finally, the parameter _β_ can be optimized according to the global objective from Lemma 2: 


![](data/pdf_cache/images/2603.14094.pdf-0014-12.png)


## **B.4. Proof of Proposition 3** 

We start from the definition of the R´enyi divergence of order _α_ for distributions _P_ and _Q_ : 


![](data/pdf_cache/images/2603.14094.pdf-0014-15.png)


For the robust expected information gain (1), we have _P_ = _p_ ( _θ_ ) _p_ ( _x | θ, ξ_ ) and _Q_ = _p_ ( _θ_ ) _pα_ ( _x | ξ_ ). Substituting leads to: 


![](data/pdf_cache/images/2603.14094.pdf-0014-17.png)


The optimal titled marginal _pα_ ( _x | ξ_ ) is defined by the _α_ -tilted marginal: 


![](data/pdf_cache/images/2603.14094.pdf-0014-19.png)


**Maximin Robust Bayesian Experimental Design** 

Substituting this form back into the integral, we obtain: 


![](data/pdf_cache/images/2603.14094.pdf-0015-02.png)


Next, we multiply and divide the inner term by _p_ ( _x | ξ_ ) _[α]_ : 


![](data/pdf_cache/images/2603.14094.pdf-0015-04.png)


The inner integral corresponds to the scaled exponential of the R´enyi divergence between posterior and prior: 


![](data/pdf_cache/images/2603.14094.pdf-0015-06.png)


## **B.5. Proof of Proposition 2** 

For the proof that follows, we require that the nominal model carries finite information content. **Assumption 1** (Finite expected surprise) **.** _The integral_ 


![](data/pdf_cache/images/2603.14094.pdf-0015-09.png)


_is well-defined and finite for all_ ( _ξ, x_ ) _. Additionally, the geometric average log-likelihood_ 

_is uniformly bounded away from_ 0 _: there exists a constant C_ 0 _>_ 0 _, such that for all ξ ∈_ Ξ _, it holds:_ 1 _≥ H_ 0( _ξ_ ) _> C_ 0 _._ 

The behavior of the robust expected information gain is driven by the multiplier _α/_ ( _α −_ 1), so it is sufficient to verify that the remaining integral term remains bounded. For this purpose, we identify _H_ 0( _ξ_ ), defined in (8), as a uniform lower bound. This bound permits a direct application of Assumption 1, from which the desired convergence result follows. Let us start by defining the pointwise quantity: 


![](data/pdf_cache/images/2603.14094.pdf-0015-13.png)


Note that _I_ ( _x, ξ_ ; _·_ ) is non-decreasing in _α_ . We determine its limit as _α →_ 0 by writing it as a ratio _f_ ( _α_ ) _/α_ : 


![](data/pdf_cache/images/2603.14094.pdf-0015-15.png)


This presents an indeterminate limit 0 _/_ 0. Applying L’Hopital’s rule, the limit corresponds toˆ lim _α→_ 0+ _f[′]_ ( _α_ ), provided it exists. The derivative is: 


![](data/pdf_cache/images/2603.14094.pdf-0015-17.png)


We analyze the denominator and numerator of _f[′]_ ( _α_ ) separately. For the denominator, Lebesgue’s dominated convergence theorem, applied with the bound _p_ ( _x | θ, ξ_ ) _[α] ≤_ max _{_ 1 _, p_ ( _x | θ, ξ_ ) _}_ , ensures convergence to 1. For the numerator, the same 

15 

**Maximin Robust Bayesian Experimental Design** 

theorem, combined with Lebesgue’s differentiation theorem applied to the derivative of the integrand: 

�� _p_ ( _x | θ, ξ_ ) _α_ log _p_ ( _x | θ, ξ_ )�� _≤_ max �1 _, p_ ( _x | θ, ξ_ )���log _p_ ( _x | θ, ξ_ )�� _,_ 

which is finite by Assumption 1, ensures that the numerator converges to 


![](data/pdf_cache/images/2603.14094.pdf-0016-04.png)


Combining these results yields the pointwise bounds for all _α ∈_ (0 _,_ 1), _x ∈X_ , and _ξ ∈_ Ξ: 


![](data/pdf_cache/images/2603.14094.pdf-0016-06.png)


Exponentiating and integrating with respect to _x_ provides 


![](data/pdf_cache/images/2603.14094.pdf-0016-08.png)


By Assumption 1, we have _H_ 0( _ξ_ ) _≥ C_ 0 _>_ 0. Consequently, the log-integral term is strictly bounded: 


![](data/pdf_cache/images/2603.14094.pdf-0016-10.png)


This bound holds uniformly in _ξ_ and _α_ . Since the multiplier _α/_ (1 _− α_ ) converges to zero, the robust expected information gain vanishes as _α →_ 0, completing the proof. 

## **B.6. Proof of Proposition 4** 

This assumption, used in Proposition 4 and Lemmata 3 and 4, controls the design objective behavior. 

**Assumption 2** (Regularity and boundedness) **.** _We assume α ∈_ (0 _,_ 1) _and that the set_ Ξ _has a finite diameter D_ Ξ _. The ratios w_ ( _x, θ, ·_ ) _[α] are Lw-Lipschitz, bounded by Cw, and have bounded variance σw_[2][:= sup] _ξ,x_[V] _[θ]_[[] _[w][α]_[]] _[.][The function][ h][ is] Lh-Lipschitz, bounded by Ch, and has bounded variance σh_[2][:= sup] _ξ_[V] _[x][|][ξ]_[[(][E] _[θ]_[[] _[w][α]_[])][1] _[/α]_[]] _[.][The function][ g][ is lower bounded] by τ >_ 0 _, implying f is Lf -Lipschitz._ 

**Lemma 3** (Bias bound for ˜ _g_ ( _ξ_ ), Hu et al., 2020) **.** _Under Assumption 2, for any design ξ ∈_ Ξ _, the bias of the estimator_ ˜ _g_ ( _ξ_ ) _is bounded by:_ 


![](data/pdf_cache/images/2603.14094.pdf-0016-16.png)


**Lemma 4** (Variance bound for _g_ ˜( _ξ_ ), Hu et al., 2020) **.** _Under Assumption 2, for any design ξ ∈_ Ξ _, the variance of the estimator_ ˜ _g_ ( _ξ_ ) _is bounded by:_ 


![](data/pdf_cache/images/2603.14094.pdf-0016-18.png)


Recall that _I_[˜] _α[S]_[(] _[ξ]_[) =] _[ f]_[(˜] _[g]_[(] _[ξ]_[))][, where the functions] _[ f]_[and] _[ g]_[ are defined in Section][ 4][.][We decompose the absolute error by] adding and subtracting the term _f_ (E[˜ _g_ ]) and then applying the triangle inequality: 


![](data/pdf_cache/images/2603.14094.pdf-0016-20.png)


We can bound the first term by applying Jensen’s inequality and invoking the Lipschitz continuity of _f_ : 


![](data/pdf_cache/images/2603.14094.pdf-0016-22.png)


then we apply the Cauchy–Schwarz inequality, E[ _|X|_ ] _≤_ �E[ _X_[2] ], and obtain: 


![](data/pdf_cache/images/2603.14094.pdf-0016-24.png)


where the variance V[˜ _g_ ] is controlled by Lemma 4. The second term can be bounded directly using Lipschitz continuity: 

�� _f_ (E[˜ _g_ ]) _− f_ ( _g_ )�� _≤ Lf_ ��E[˜ _g_ ] _− g_ �� _,_ 

where ��E[˜ _g_ ] _− g_ �� is bounded by Lemma 3. Finally, combining these two bounds yields the stated result. 

16 

**Maximin Robust Bayesian Experimental Design** 

## **B.7. Proof of Proposition 5** 

We briefly state a two-sided version of Hoeffding’s inequality for bounded random variables that aids in the proof. 

**Lemma 5** (Two-sided Hoeffding inequality for bounded random variables, Vershynin, 2018) **.** _Let X_ 1 _, . . . , XN be independent random variables such that Xi ∈_ [ _ai, bi_ ] _for every i ∈{_ 1 _, . . . , N }. Then, for any t >_ 0 _, we have_ 


![](data/pdf_cache/images/2603.14094.pdf-0017-04.png)


> Recall that _I_[˜] _α[S]_[(] _[ξ]_[) =] _[ f]_[(˜] _[g]_[(] _[ξ]_[))][, where the functions] _[ f]_[and] _[ g]_[ are defined in Section][ 4][.][By inovking the Lipschitz continuity of] _f_ and applying the triangle inequality, we decompose the total error into a _stochastic_ and _deterministic_ component: 


![](data/pdf_cache/images/2603.14094.pdf-0017-06.png)


According to Lemma 3, the deterministic term ��E[˜ _g_ ] _− g_ �� is upper bounded by _Lhσw/√M_ . To ensure the total error stays within tolerance _t_ , we constrain this error term to consume at most half of the total budget _t/_ 2 by choosing _M_ such that: 


![](data/pdf_cache/images/2603.14094.pdf-0017-08.png)


˜ Consequently, for the total error to exceed _t_ , the stochastic term �� _g −_ E[˜ _g_ ]�� must account for the remaining difference: 


![](data/pdf_cache/images/2603.14094.pdf-0017-10.png)


> Next, we bound the probability of this deviation. _h_ ˜[(] _[i]_[)] , defined as: Recall that ˜ _g_ is the empirical average of _N_ independent random variables 


![](data/pdf_cache/images/2603.14094.pdf-0017-12.png)


By Assumption 2, the function _h_ is bounded by _Ch_ , implying that each random variable _h_[˜][(] _[i]_[)] _∈_ [0 _, Ch_ ]. We can therefore _N_ apply Lemma 5 to the sample average ˜ _g_ = _N_[1] � _i_ =1 _[h]_[˜][(] _[i]_[)][:] 


![](data/pdf_cache/images/2603.14094.pdf-0017-14.png)


Combining the bounds on the stochastic and deterministic components, we obtain the final concentration inequality: 


![](data/pdf_cache/images/2603.14094.pdf-0017-16.png)


## **B.8. Proof of Proposition 6** 

This proof follows standard PAC-Bayes proof techniques presented by Alquier (2024). We begin by stating three useful lemmas that will facilitate the derivation. 

**Lemma 6** (Moment generating function of sub-Gaussian random variables, Vershynin, 2018) **.** _Let X be a sub-Gaussian random variable such that_ P( _|X| ≥ t_ ) _≤_ 2 exp _{−t_[2] _/C_[2] _}. Then, for any λ >_ 0 _, it holds that:_ 

E �exp _{λ X}_ � _≤_ exp _{λ_[2] _C_[2] _}._ 

**Lemma 7** (Markov inequality, Vershynin, 2018) **.** _For any nonnegative random variable X and a >_ 0 _, we have_ 


![](data/pdf_cache/images/2603.14094.pdf-0017-22.png)


**Maximin Robust Bayesian Experimental Design** 

**Lemma 8** (Donsker–Varadhan variational formula, Donsker & Varadhan, 1975) **.** _For any measurable, bounded function f_ : Ξ _�→_ R _, and any probability measure π_ 0 _∈_ Π _, we have:_ 


![](data/pdf_cache/images/2603.14094.pdf-0018-02.png)


To prove the proposition, we first analyze the concentration properties of the estimation error _I_[˜] _α[S]_[(] _[ξ]_[)] _[ −][I] α[S]_[(] _[ξ]_[)][.][By invoking] Proposition 5, for a tolerance _t >_ 0, and assuming _M ≥_ 4 _L_[2] _f[L] h_[2] _[σ] w_[2] _[/t]_[2][, the estimator bias admits a sub-Gaussian tail bound:] 


![](data/pdf_cache/images/2603.14094.pdf-0018-04.png)


Using Lemma 6 on this random variable, for any _λ >_ 0, we have: 

where the outer expectation is evaluated under the sample distribution of the naive nested Monte Carlo estimator. We integrate this bound under the policy _π_ 0 and swap the expectations yielding: 


![](data/pdf_cache/images/2603.14094.pdf-0018-07.png)


Next, we apply Lemma 8 to the inner expectation and obtain the following: 


![](data/pdf_cache/images/2603.14094.pdf-0018-09.png)


This gives us a bound on the expectation of the form: E[ _X_ ] _≤ b_ , where _X_ is the exponential term inside the outer expectation. To convert this expectation bound back to a probability bound, we apply Lemma 7 on _X_ and assume _k_ = 1 _/δ_ for _δ ∈_ (0 _,_ 1): 


![](data/pdf_cache/images/2603.14094.pdf-0018-11.png)


that holds with a probability at least 1 _− δ_ . 

Finally, the condition _M ≥_ 4 _L_[2] _f[L] h_[2] _[σ] w_[2] _[/t]_[2][required for the sub-Gaussian concentration inequality to be valid fo a given] tolerance _t_ translates to _M ≥_ 2 _NL_[2] _h[σ] w_[2] _[/]_[(] _[C] h_[2][log(2] _[/δ]_[))][ to achieve a confidence probability][ 1] _[ −][δ]_[.] 

## **C. Implementation of the Nested Monte Carlo Estimator** 

To ensure numerical stability and prevent arithmetic underflow, we perform all computations strictly in the logarithmic domain. We define the log-likelihood function as _ℓ_ ( _θ, x_ ) := log _p_ ( _x | θ, ξ_ ) and the log-sum-exp operator as LSE( _y_ 1: _K_ ) := log[�] _[K] k_ =1[exp(] _[y][k]_[)][.][The estimation procedure proceeds in four steps:] 

> • We first generate an outer batch of _N_ independent ( _θ, x_ ) pairs from the joint generative model. For each outer sample with index _i ∈{_ 1 _, . . . , N }_ , we independently draw a set of _M_ auxiliary parameters from the prior to serve as contrastive samples for the marginal likelihood estimation: 


![](data/pdf_cache/images/2603.14094.pdf-0018-17.png)


18 

**Maximin Robust Bayesian Experimental Design** 

- As per Corollary 2, we now need to compute _w_ ( _x_[(] _[i]_[)] _, θ_[(] _[i,j]_[)] _, ξ_ ) = _p_ ( _x_[(] _[i]_[)] _| θ_[(] _[i,j]_[)] _, ξ_ ) _/p_ ( _x_[(] _[i]_[)] _| ξ_ ) =: _w_[(] _[i,j]_[)] . We approximate the log-marginal likelihood using the auxiliary samples in _θ_ to obtain the following estimator for _w_[(] _[i,j]_[)] : 


![](data/pdf_cache/images/2603.14094.pdf-0019-02.png)


- We next estimate the inner expectation term _ℓ_ ( _x_ ) = E _p_ ( _θ_ )[ _w_ ( _x, θ, ξ_ ) _[α]_ ] by averaging the powered weights. In the log-domain, this corresponds to a second application of the LSE operator over the _M_ inner samples: 


![](data/pdf_cache/images/2603.14094.pdf-0019-04.png)


- Finally, we compute the robust expected information gain by aggregating the outer samples. The estimator _I_[˜] _α[S]_[(] _[ξ]_[)] approximates the logarithm of the expected exponential gain: 


![](data/pdf_cache/images/2603.14094.pdf-0019-06.png)


This procedure yields a consistent, albeit biased, estimate of the robust objective. 

## **D. Theoretical Comparison of PAC-Bayesian Policies and Deterministic Policies** 

The theoretical advantages of PAC-Bayesian bounds are comprehensively summarized in Alquier (2024). In the context of bandit problems, which are highly relevant to experimental design, stochastic policies derived from the PAC-Bayesian formulation facilitate efficient exploration while streamlining the theoretical analysis (Flynn et al., 2023). This section aims to compare the concentration properties of deterministic and stochastic policies, illustrating that PAC-Bayesian bounds can yield a sharper upper estimate of the minimum of the information gain under certain conditions. These results further reinforce the preference for stochastic policies, as they do not necessarily compromise the concentration rate in spite of the induced randomness, while leveraging the theoretical versatility of the PAC-Bayesian framework. 

Consider the minimization of an objective function _J_ ( _ξ_ ) over the design space Ξ, where the analysis applies symmetrically to maximization. To streamline the illustration, we adopt a simplified setup where the objective function _J_ ( _ξ_ ) is defined by _J_ ( _ξ_ ) = E _z∼p_ [ _h_ ( _ξ, z_ )], where _h_ ( _ξ, ·_ ) is an integrand with a latent variable _z_ defined on a compact support _Z ⊂_ R _[k]_ and _p_ is the distribution of the latent variable _z_ . We approximate the objective function _J_ ( _ξ_ ) using the empirical Monte Carlo estimator _J_[˜] ( _ξ_ ) defined by _N_ i.i.d. realizations _z_ 1 _, . . . , zN_ drawn from _p_ : 


![](data/pdf_cache/images/2603.14094.pdf-0019-11.png)


While we seek to minimize _J_ ( _ξ_ ), the exact objective function _J_ ( _ξ_ ) is inaccessible in practice. Consequently, the deterministic policy minimizes the Monte Carlo estimator _J_[˜] ( _ξ_ ) as a proxy. We define 


![](data/pdf_cache/images/2603.14094.pdf-0019-13.png)


One justification for employing the deterministic policy is that the minimum of the Monte Carlo estimator _J_[˜] ( _ξ_ ) provides an upper estimate of the global minimum _J_ ( _ξ_ min). 

To derive the upper estimate, we introduce a standard measure from statistical learning theory, called the Rademacher complexity. Intuitively, the Rademacher complexity measures the expressive power of a function family relative to samples of size _N_ . Let _RN_ denote the Rademacher complexity of the integrand family _{h_ ( _·, z_ ) _| z ∈Z}_ computed over _N_ random samples _{zi}[n] i_ =1[following] _[ p]_[.][For the purposes of this illustration, the formal definition of Rademacher complexity is omitted] for brevity. We refer the reader to Wainwright (2019) for a rigorous treatment of Rademacher complexity and its established upper bounds for common function classes. The next assumption is used throughout this section. 

**Assumption 3.** _The integrand h_ ( _ξ, z_ ) _is non-negative, continuous, and uniformly bounded by a constant b. The objective function J_ ( _ξ_ ) _is uniquely minimized over_ Ξ _._ 

The following upper estimate of the global minimum _J_ ( _ξ_ min) is a standard result derived from empirical process theory, particularly in the study of empirical risk minimization. 

19 

**Maximin Robust Bayesian Experimental Design** 

**Proposition 7.** _It holds for any N >_ 0 _and δ >_ 0 _that_ 


![](data/pdf_cache/images/2603.14094.pdf-0020-02.png)


_where the minimum is attained at ξ_ = _ξ_[˜] _min._ 

_Proof._ We have _J_ ( _ξ_ min) _≤ J_ ( _ξ_ ) for any point _ξ_ , since _ξ_ min is the minima. This, in turn, yields that 


![](data/pdf_cache/images/2603.14094.pdf-0020-05.png)


The following concentration inequality is a direct result of Theorem 4.10 of Wainwright (2019): 


![](data/pdf_cache/images/2603.14094.pdf-0020-07.png)


Rearranging the term completes the proof. 

By definition, the empirical minimizer _ξ_[˜] min yields the sharpest possible bound of this form, as any deviation from the empirical minima necessarily increases the value of the upper estimate. 

In contrast to the above concentration inequality, the PAC-Bayesian framework provides a flexible upper estimate that bypasses the need for global complexity measures such as the Rademacher complexity. Given a prior _π_ 0 over the design space Ξ, we define a stochastic (Gibbs) policy _π∗_ as 


![](data/pdf_cache/images/2603.14094.pdf-0020-11.png)


where _λ >_ 0 is the precision hyperparameter that controls the dispersion of the policy. A well-established bound by Catoni (2007) provides the following upper estimate under the stochastic policy _π∗_ . 

**Proposition 8.** _It holds for any N >_ 0 _and δ >_ 0 _that_ 


![](data/pdf_cache/images/2603.14094.pdf-0020-14.png)


_where the minimum is attained at ρ_ = _π∗._ 

_Proof._ We have _J_ ( _ξmin_ ) _≤_ E _ρ_ [ _J_ ( _ξ_ )] for an arbitrary distribution _ρ_ , since _ξmin_ is the minima and _J_ is non-negative. Applying the Catoni’s bound (Catoni, 2007) to the expectation E _ρ_ [ _J_ ( _ξ_ )] completes the proof. 

Employing the stochastic policy offers two primary benefits: (i) it permits a more tractable and flexible theoretical treatment by circumventing dependency on global complexity measures, and (ii) it promotes exploration across the design space Ξ, as discussed in Flynn et al. (2023). Furthermore, it may yield a sharper upper estimate of the global minimum _J_ ( _ξ_ min) than the standard bound. Finally, the following proposition demonstrates that the PAC-Bayesian bound can be strictly sharper than the other, provided that the level _δ_ and the precision parameter _λ_ are appropriately chosen. 


![](data/pdf_cache/images/2603.14094.pdf-0020-18.png)


_Proof._ By the Donsker-Varadhan variational formula from Lemma 8, we have 


![](data/pdf_cache/images/2603.14094.pdf-0020-20.png)


20 

**Maximin Robust Bayesian Experimental Design** 

It follows from the upper bound of _J_ ˜( _ξ_ ) _≤ b ≤ J_ ˜(˜ _ξ_ min) + 2 _RN_ + (1 _/ δ_ 4) that _b_ �2 log(1 _b ≤ b_ ( _/δ_ 1 _/_ )4 _/N_ )�.2 log(1Substituting this into the Donsker–Varadhan formula gives that _/δ_ ) _/N_ . Since _J_[˜] is non-negative and bounded by _b_ , we have 


![](data/pdf_cache/images/2603.14094.pdf-0021-02.png)


Thus, to establish the main result, it suffices to show that 

Solving the quadratic inequality on the right hand side completes the proof. 

This comparison is not intended to suggest that the PAC-Bayesian framework generally yields a sharper bound than the classical counterparts; their performance remains contingent on the choice of prior and the concentration of the empirical objective. Nevertheless, it illustrates that the PAC-Bayesian framework can provide the latitude to enhance concentration properties, while offering flexibility in the theoretical analysis. In this illustration, for some confidence level _δ_ , there exists a regime of the precision parameter _λ_ where the PAC-Bayesian bound is strictly sharper than the other bound. Such theoretical insights may further facilitate a principled selection of the precision parameter _λ_ in practice. 

## **E. Evaluation Details** 

## **E.1. Linear Regression** 

To illustrate the robust experimental design framework, we derive closed-form expressions for the worst-case distribution and robust expected information gain in the conjugate linear regression setting. This model admits tractable analytical results that provide intuition for the general case. 

Consider the standard Bayesian linear regression model. Let _θ_ = ( _θ_ 1 _, θ_ 2) _[⊤] ∈_ R[2] denote the unknown parameter vector, where _θ_ 1 _∈_ R is the slope and _θ_ 2 _∈_ R is the offset. We endow _θ_ with a Gaussian prior _p_ ( _θ_ ) = N( _θ_ ; _µ_ 0 _,_ Σ0), where _µ_ 0 _∈_ R[2] is the prior mean and Σ0 _∈_ R[2] _[×]_[2] is the prior covariance matrix. A batch design _ξ_ 1: _N_ = ( _ξ_ 1 _, . . . , ξN_ ) _∈_ Ξ specifies _N_ individual designs _ξi ∈_ R. We construct the augmented design matrix _H_ ( _ξ_ 1: _N_ ) _∈_ R _[N][×]_[2] by appending a column of ones: 


![](data/pdf_cache/images/2603.14094.pdf-0021-10.png)


Conditioned on the parameter _θ_ and design _ξ_ 1: _N_ , the _N_ measurements are collected as a vector _x_ 1: _N_ = ( _x_ 1 _, . . . , xN_ ) _[⊤] ∈_ R _[N]_ , where each _xi ∈_ R is a scalar observation. Under the assumption of independence, the likelihood factorizes as: 


![](data/pdf_cache/images/2603.14094.pdf-0021-12.png)


where _σ_[2] _>_ 0 is the observation noise variance. 

**Marginal and posterior.** Under these conjugate assumptions, the marginal likelihood admits closed-form Gaussian expressions: 


![](data/pdf_cache/images/2603.14094.pdf-0021-15.png)


Additionally, the posterior _p_ ( _θ | x_ 1: _N , ξ_ 1: _N_ ) = N( _θ_ ; _µN ,_ Σ _N_ ) is given by the standard conjugate update formulas: 


![](data/pdf_cache/images/2603.14094.pdf-0021-17.png)


**Worst-case distribution.** The worst-case joint distribution _q[⋆]_ ( _θ, x_ 1: _N | ξ_ 1: _N_ ) is given by: 


![](data/pdf_cache/images/2603.14094.pdf-0021-19.png)


21 

**Maximin Robust Bayesian Experimental Design** 


![](data/pdf_cache/images/2603.14094.pdf-0022-01.png)


**----- Start of picture text -----**<br>
α  = 0 . 01 α  = 0 . 10 α ≈ 1 . 00<br>1<br>− 1<br>2<br>ξ<br>**----- End of picture text -----**<br>


_Figure 4._ Robust expec _−_ ~~ted information gain for a t~~ 1 1 wo-d _−_ ~~imensional linear regressio~~ 1 1 n pro _−_ ~~blem with a correlated prio~~ 1 1 r, as a function of _α ∈_ (0 _,_ 1). Contour lines depict the objective landscape over _ξ_ 1 ( _ξ_ 1 _, ξ_ 2), highlighting how the optimal designs ( _ξ_ 1 _ξ_ 1 _⋆_ ) shift with _α_ . where the tilted marginal _pα_ ( _x_ 1: _N | ξ_ 1: _N_ ) is defined as: 


![](data/pdf_cache/images/2603.14094.pdf-0022-03.png)


For this conjugate problem, the _α_ -powered likelihood is: 


![](data/pdf_cache/images/2603.14094.pdf-0022-05.png)


where _∥x_ 1: _N − H_ ( _ξ_ 1: _N_ ) _θ∥_[2] =[�] _[N] i_ =1[(] _[x][i][ −][ξ][i][θ]_[1] _[ −][θ]_[2][)][2][.][To compute the expectation][ E] _[p]_[(] _[θ]_[)] � _p_ ( _x_ 1: _N | θ, ξ_ 1: _N_ ) _[α]_[�] , we expand the quadratic form and integrate over _θ_ . Completing the square in _θ_ yields: 


![](data/pdf_cache/images/2603.14094.pdf-0022-07.png)


where we define the tilted covariance matrix and mean: 

After simplification the tilted marginal takes the form: 


![](data/pdf_cache/images/2603.14094.pdf-0022-10.png)


where Λ _α_ is the _α_ -scaled predictive covariance for the batch: 


![](data/pdf_cache/images/2603.14094.pdf-0022-12.png)


Therefore, the tilted marginal is Gaussian: 


![](data/pdf_cache/images/2603.14094.pdf-0022-14.png)


Overall, this results in a worst-case joint distribution _q[⋆]_ ( _θ, x_ 1: _N | ξ_ 1: _N_ ) that is also Gaussian: 


![](data/pdf_cache/images/2603.14094.pdf-0022-16.png)


with mean and covariance: 


![](data/pdf_cache/images/2603.14094.pdf-0022-18.png)


where the worst-case posterior _q[⋆]_ ( _θ | x_ 1: _N , ξ_ 1: _N_ ) = N( _θ_ ; _µ[⋆] θ[,]_[ Σ] _[⋆] θ_[)][ is:] 

**Maximin Robust Bayesian Experimental Design** 

**Sibson’s mutual information.** Finally, for this conjugate setting, Sibson’s _α_ -mutual information admits a closed-form expression. Using the definition 


![](data/pdf_cache/images/2603.14094.pdf-0023-02.png)


which corresponds to the log-normalizer of _pα_ ( _x_ 1: _N | ξ_ 1: _N_ ): 

As _α →_ 1, the robust expected information gain recovers Shannon’s mutual information, which is the standard result for Bayesian linear regression with _N_ measurements. As _α →_ 0, the term _[σ] α_[2] _[I][N]_[dominates, and all designs become equally] uninformative, consistent with Proposition 2. 

**Renyi´ divergence.** The Renyi´ divergence between two Gaussian distribution is useful because it provides tractable computation of the realized robust information gain conditioned on a design and measured outcome. We derive the closedform for orders _α ∈_ (0 _,_ 1). Let’s assume two Gaussian distributions _q_ ( _θ_ ) = N( _θ_ ; _µq,_ Σ _q_ ) and _p_ ( _θ_ ) = N( _θ_ ; _µp,_ Σ _p_ ). The divergence is defined as: 


![](data/pdf_cache/images/2603.14094.pdf-0023-06.png)


Substituting the Gaussian density functions, the integrand becomes a product of exponential quadratic forms. The exponent corresponds to a new quadratic form defined by the geometric mixture of the parameters. Let Σ _α_ and _µα_ denote the covariance and mean of this geometric mixture, defined by the weighted sum of precision matrices: 


![](data/pdf_cache/images/2603.14094.pdf-0023-08.png)


Evaluating the Gaussian integral yields the log-integral term: 

where _Zα_ is defined as follows: 


![](data/pdf_cache/images/2603.14094.pdf-0023-11.png)


Finally, scaling by 1 _/_ ( _α −_ 1) gives the divergence: 


![](data/pdf_cache/images/2603.14094.pdf-0023-13.png)


## **E.2. A/B Testing** 

To illustrate the robust experimental design framework in a setting with discrete measurements, we derive expressions for the worst-case distribution and robust expected information gain in the conjugate Beta-Binomial A/B testing setting. 

Consider a standard A/B testing scenario where we wish to infer the conversion rates of two independent variants. Let _θ_ = ( _θa, θb_ ) _[⊤] ∈_ [0 _,_ 1] _×_ [0 _,_ 1] denote the unknown parameter vector, where _θa_ and _θb_ are the conversion probabilities for groups A and B, respectively. We equip _θ_ with a product of independent Beta priors: 


![](data/pdf_cache/images/2603.14094.pdf-0023-17.png)


where _δa, γa, δb, γb >_ 0 are the prior hyperparameters. A design _ξ_ = ( _na, nb_ ) _∈_ Ξ specifies the sample sizes allocated to each group, subject to a total budget constraint _na_ + _nb_ = _N_ . The measurements _x_ = ( _xa, xb_ ) _∈{_ 0 _, . . . , na}×{_ 0 _, . . . , nb}_ represent the number of conversions, or successes, in each group. Under the assumption of independence, the likelihood factorizes as a product of Binomial distributions: 


![](data/pdf_cache/images/2603.14094.pdf-0023-19.png)


23 

**Maximin Robust Bayesian Experimental Design** 


![](data/pdf_cache/images/2603.14094.pdf-0024-01.png)


**----- Start of picture text -----**<br>
α  = 0 . 01 α  = 0 . 10 α ≈ 1 . 00<br>× 10 [−] [2]<br>0 . 2 1<br>2<br>0 . 1 0 . 5<br>1<br>0 0 0<br>Figure 5. Robust expected information gain as a function of0 10 20 0  α ∈ 10(0 ,  1) for an A/B testing problem with 25 participants.20 0 10 20 The optimal<br>allocation, highlighted in dark gray, shifts as ξ  α  varies. ξ ξ<br>**----- End of picture text -----**<br>


**Marginal and posterior.** Under these assumptions, we can derive the marginal likelihood of the measurements _p_ ( _x | ξ_ ) by integrating out the parameters _θ_ . This results in the Beta-Binomial distribution. For a single group _k ∈{a, b}_ , the marginal probability of observing _xk_ successes in _nk_ trials is: 


![](data/pdf_cache/images/2603.14094.pdf-0024-03.png)


where _B_ ( _·_ ) is the Beta function and the joint marginal likelihood is simply the product _p_ ( _x | ξ_ ) = _p_ ( _xa | na_ ) _p_ ( _xb | nb_ ). 

Furthermore, under the assumptions of conjugacy, we can compute the Bayes posterior _p_ ( _θ | x, ξ_ ) in closed-form as factorized independent Beta distributions for each group. For _k ∈{a, b}_ : 


![](data/pdf_cache/images/2603.14094.pdf-0024-06.png)


**Worst-case distribution.** The worst-case joint distribution _q[⋆]_ ( _θ, x | ξ_ ) is given by: 


![](data/pdf_cache/images/2603.14094.pdf-0024-08.png)


where the _α_ -tilted marginal _pα_ ( _x | ξ_ ) is defined as: 


![](data/pdf_cache/images/2603.14094.pdf-0024-10.png)


For this conjugate problem, we compute the expectation of the _α_ -powered likelihood. Due to independence, the expectation factorizes over the categories for _θa_ and _θb_ : 


![](data/pdf_cache/images/2603.14094.pdf-0024-12.png)


Focusing on a single group with parameters ( _θk, nk, xk_ ) where _k ∈{a, b}_ : 


![](data/pdf_cache/images/2603.14094.pdf-0024-14.png)


The expectation with respect to the Beta prior is: 

24 

**Maximin Robust Bayesian Experimental Design** 

Let us define the auxiliary term _Zα,k_ ( _xk, nk_ ) as this expectation: 


![](data/pdf_cache/images/2603.14094.pdf-0025-02.png)


The _α_ -tilted marginal _pα_ ( _x | ξ_ ) then takes the form: 


![](data/pdf_cache/images/2603.14094.pdf-0025-04.png)


To normalize this distribution, we compute the partition function: 


![](data/pdf_cache/images/2603.14094.pdf-0025-06.png)


Consequently, the worst-case joint distribution _q[⋆]_ ( _θ, x | ξ_ ) implies a worst-case posterior _q[⋆]_ ( _θ | x, ξ_ ) which is the _α_ -tilted posterior. For the Beta-Binomial model, this results in a Beta distribution with updated parameters: 


![](data/pdf_cache/images/2603.14094.pdf-0025-08.png)


This confirms that under model misspecification, _α <_ 1, the experimenter updates beliefs less aggressively than in the standard Bayesian setting. 

**Sibson’s** _α_ **-mutual information.** Sibson’s _α_ -mutual information can be written as: 


![](data/pdf_cache/images/2603.14094.pdf-0025-11.png)


Substituting our derived terms, this becomes _Iα[S]_[(] _[ξ]_[) =] _[ α/]_[(] _[α][ −]_[1) log] _[ Z][α]_[(] _[ξ]_[)][.][Due to the independence of the groups, the] information gain is additive _Iα[S]_[(] _[ξ]_[) =] _[ I] α[S]_[(] _[n][a]_[) +] _[ I] α[S]_[(] _[n][b]_[)][, were the contribution of a single group with allocation] _[ n][k]_[is:] 


![](data/pdf_cache/images/2603.14094.pdf-0025-13.png)


As _α →_ 1, we recover the standard expected information gain for the Beta-Binomial model, which corresponds to Shannon’s mutual information. As _α →_ 0, the robust information gain approaches zero. 

**Renyi divergence.´** Similar to the Gaussian case, the Renyi divergence between two Beta distributions admits a closed-form´ expression, which allows for tractable computation of the realized robust information gain given a design and outcome. Consider two Beta distributions _q_ ( _θ_ ) = Beta( _θ_ ; _δq, γq_ ) and _p_ ( _θ_ ) = Beta( _θ_ ; _δp, γp_ ). The divergence of order _α_ is: 


![](data/pdf_cache/images/2603.14094.pdf-0025-16.png)


Substituting the Beta density functions, the integrand becomes a product of power functions. This results in an unnormalized Beta density with a geometric mixture of the original parameters. Let _δα_ and _γα_ denote the effective parameters of this mixture, defined by the linear interpolation of the natural parameters: 


![](data/pdf_cache/images/2603.14094.pdf-0025-18.png)


The integral can then be evaluated analytically using the Beta function _B_ ( _·_ ): 


![](data/pdf_cache/images/2603.14094.pdf-0025-20.png)


Taking the logarithm and scaling by 1 _/_ ( _α −_ 1) yields the closed-form divergence: 


![](data/pdf_cache/images/2603.14094.pdf-0025-22.png)


## **F. Variations of** _α_ **-Mutual Information** 

The choice between the Lapidoth–Pfister, Sibson, and Csiszar´ _α_ -mutual information measures constitutes a fundamental decision-theoretic stance. Each choice specifies a different adversarial game between the experimenter and nature, and 

25 

**Maximin Robust Bayesian Experimental Design** 

thereby determines which elements of the data-generating process are subject to adversarial distortion and which elements of the experimenter’s nominal belief are held fixed. 

For the purposes of this discussion, we set aside stochastic policies and restrict attention to explicit deterministic designs. Adapting the definitions of _α_ -mutual information from (Esposito et al., 2024) to the experimental design setting, we discuss these distinctions by expressing each measure as the value of a minimization problem over the ambiguity set _Qρ_ ( _ξ_ ): 


![](data/pdf_cache/images/2603.14094.pdf-0026-03.png)


The Lapidoth–Pfister mutual information _Iα_[LP] (Lapidoth & Pfister, 2019) corresponds to the most agnostic stance. Nature is free to manipulate the full joint in order to minimize the information over the ambiguity set, while the marginal decomposition is optimized to match the worst-case marginals: 


![](data/pdf_cache/images/2603.14094.pdf-0026-05.png)


This metric evaluates an experiment’s ability to recover _θ_ under worst-case conditions, irrespective of whether the assumed parameter _θ_ is plausible under the experimenter’s nominal prior _p_ ( _θ_ ). Although this yields maximal robustness in a purely information-theoretic sense, this measure can be too pessimistic for Bayesian experimental design. In particular, it allows nature to expend its entire budget _ρ_ on shifting the marginal _q_ ( _θ_ ) far from the experimenter’s prior, so that the resulting measurements become effectively uninformative even when the likelihood is otherwise well-specified. Designs optimized under this objective may therefore contribute little to refining the experimenter’s actual beliefs. 

At the other extreme lies the Csiszar´ _α_ -mutual information (Csiszar´ , 2002), which corresponds to a likelihood-robust utility. Here, the experimenter trusts their prior implicitly, constraining nature to a subset of the ambiguity set _Wρ_ ( _ξ_ ) _⊂Qρ_ ( _ξ_ ) where the marginal distribution of the parameters must match the nominal exactly: 


![](data/pdf_cache/images/2603.14094.pdf-0026-08.png)


Because nature is not allowed to alter the parameter marginal, its budget _ρ_ is spent entirely on distorting the likelihood. While this protects against model misspecification, it leaves the experimenter completely vulnerable to prior miscalibration. If the true parameter value lies in a region that the nominal prior assigns very small probability to, an experimenter using _Iα[C]_ as an objective may fail to design experiments that account for this risk. 

Finally, Sibson’s _α_ -mutual information (Sibson, 1969) appears to occupy the decision-theoretic middle ground. Like Lapidoth–Pfister, nature is allowed to minimize the information gain over the full ambiguity set, and therefore may distort ´ the joint distribution _q_ ( _θ, x | ξ_ ). At the same time, in the spirit of Csiszar’s measure, Sibson’s definition anchors the marginal parameter distribution to the nominal prior _p_ ( _θ_ ): 


![](data/pdf_cache/images/2603.14094.pdf-0026-11.png)


This structure explicitly acknowledges that misspecification may include prior miscalibration, while preventing nature from drifting too far from the experimenter’s hypothesis space. Because deviations of _q_ ( _θ_ ) from _p_ ( _θ_ ) are penalized through an additional KL term (3), nature must allocate its finite budget _ρ_ between distorting the prior and distorting the likelihood, rather than concentrating all of its effort on either component alone. As a consequence, designs optimized under _Iα[S]_[remain] informative specifically with respect to the experimenter’s original prior beliefs. Scenarios in which the true parameter lies far outside _p_ ( _θ_ ) are penalized, but not entirely ignored, allowing the experimenter to hedge against that risk. 

26 

