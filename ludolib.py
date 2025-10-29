import  numpy               as np
import  multiprocessing     as mp
import  GWFish              as gw
from    pathlib             import Path
from    itertools           import product

POINTS_RA_DEC   = 100           # number of points for each ra and dec, total number of points = POINTS_RA_DEC**2
POINTS_PSI      = 100           # number of points for psi, total number of points = POINTS_PSI
AVERAGE_PSI     = True          # wheter to set psi to it's average value or not, if True averages psi over POINTS_PSI (Gives a fast approximation of the average SNR over psi)
LW_APPROX       = False         # whether to use the long wavelength approximation or not
DEFAULT_GEOTIME = 1395964818    # default geocentric time

def generate_args_list(n_points = POINTS_RA_DEC, n_psi = POINTS_PSI, average_psi = True):
    '''
    Generates a list of dictionaries with the parameters for the signal. The parameters are:
    - ra: Right Ascension
    - dec: Declination
    - psi: Polarization angle  
    '''
    ra      = np.random.uniform(0., 2 * np.pi, n_points)
    dec     = np.arcsin(np.random.uniform(-1, 1, n_points))
    psi     = []
    if average_psi:
        psi = [np.mean(np.random.uniform(0., 2 * np.pi, n_psi) )] # psi taken as average
    else:
        psi = np.random.uniform(0., 2 * np.pi, n_psi)

    ra_dec          = list(zip(ra, dec))
    params_prod     = product(psi, ra_dec)

    params_list_of_dicts = [
        {
            "ra" : ra_val,
            "dec" : dec_val,
            "psi" : psi_val,
            "geocent_time": 1395964818,
        } for psi_val, (ra_val, dec_val) in params_prod
    ]

    return params_list_of_dicts

def make_fft(time_array, time_series):
    duration        = np.max(time_array) -  np.min(time_array)
    fft_transform   = np.fft.rfft(time_series, norm='forward') * duration # multiply by dt to match integral FFT
    freq_array      = np.fft.rfftfreq(len(time_array), d=np.mean(np.diff(time_array)))
    return freq_array, fft_transform

def make_ifft(time_array, freq_series):
    duration = np.max(time_array) -  np.min(time_array)
    ifft_transform  = np.fft.irfft(freq_series, n=len(time_array), norm='forward') / duration
    return ifft_transform

def _fd_phase_correction_and_output_format_from_stain_series(f_, hp, hc, geo_time = DEFAULT_GEOTIME):
    '''
    Prepares the polarizations for GWFish projection function. Combining 
    the functions "_fd_phase_correction_geocent_time", "_fd_gwfish_output_format" as in LALFD_Waveform class from waveforms.py module.

    Parameters
    ----------
    f_ : array
        Frequency array
    hp : array
        Plus polarization
    hc : array
        Cross polarization
    geo_time : int, optional
        Geocentric time
    
    Returns
    -------
    array
        Polarizations in form (hp, hc)
    '''
    phi_in          = np.exp( 1.j * (2 * f_ * np.pi * geo_time) ).T[0]
    fft_dat_plus    = phi_in*np.conjugate( hp )
    fft_dat_cross   = phi_in*np.conjugate( hc )

    # GW Fish format for hfp and hfc
    hfp             = fft_dat_plus[:, np.newaxis]
    hfc             = fft_dat_cross[:, np.newaxis]
    polarizations   = np.hstack((hfp, hfc))

    return polarizations

def get_SNR_from_series(f_in, hp, hc, network, parameters, long_wavelength_approx = LW_APPROX, geo_time = DEFAULT_GEOTIME):

        '''
        Given a set of parameters, polarizations, network, timevector and frequency array, returns the SNR associated to the signal

        Parameters
        ----------
        f_in : array
            Frequency array on which to evaluate the signal
        hp : array
            Plus polarization without geocentric time phase corrections
        hc : array
            Cross polarization without geocentric time phase corrections
        network : gw.detection.DetectorNetwork
            Detector Network object
        params : dict
            Parameters of the event, needs to include ra, dec, psi
        geo_time : int, optional
            Geocentric time
        long_wavelength_approx : bool, optional
            Whether to use the long wavelength approximation or not

        Returns
        -------
        float
            Total signal-to-Noise Ratio 
        '''
            
        polarizations   = _fd_phase_correction_and_output_format_from_stain_series(f_in, hp, hc)   
        timevector      = np.ones( len(f_in) ) * geo_time

        snrs_series = {}
        for detector in network.detectors:
            detector.frequencyvector    = f_in
            signal                      = gw.detection.projection(
                parameters, 
                detector, 
                polarizations, 
                timevector, 
                long_wavelength_approx = long_wavelength_approx)
            component_SNRs              = gw.detection.SNR(detector, signal, frequencyvector=np.squeeze(f_in))
            snrs_series[detector.name]  = np.sqrt(np.sum(component_SNRs**2))

        out_SNR = np.sqrt(np.sum([snrs_series[detector.name]**2 for detector in network.detectors]))
        return out_SNR

def snr_func(f_in, hp_f, hc_f, network, params, long_wavelength_approx = LW_APPROX):
    
    # skip f = 0 (the mean) if it exists
    f_input = f_in
    hp_f_in = hp_f
    hc_f_in = hc_f
    if f_in[0] == 0:
        f_input = f_in[1:]
        hp_f_in = hp_f_in[1:]
        hc_f_in = hc_f_in[1:]

    total_SNRs = get_SNR_from_series(f_input, hp_f_in, hc_f_in, network, params, long_wavelength_approx=long_wavelength_approx)
    return params["ra"], params["dec"], total_SNRs

def calculate_snr(f_in, hp_freq, hc_freq, network, params_list, lwa_approx = LW_APPROX):
    args_list = [(f_in, hp_freq, hc_freq, network, params, lwa_approx) for params in params_list] 
    with mp.Pool() as pool:
        snr_sub = pool.starmap(snr_func, args_list)
    return snr_sub

def calculate_network(freq, hp, hc, detectors, params, config = None, lwa_approx = LW_APPROX):
    if config:
        network = gw.detection.Network(detector_ids = detectors, config = config)
    else:
        network = gw.detection.Network(detector_ids = detectors)
    snr_sub = calculate_snr(freq[:, None], hp, hc, network, params, lwa_approx = lwa_approx)
    return snr_sub

def calculate_detector_projections(
    detector_ids: list[str],
    hp_f        : np.ndarray,
    hc_f        : np.ndarray,
    freqs       : np.ndarray,
    sky_params  : dict,
    lwa_approx  : bool = LW_APPROX,
    config      : Path = None,
) -> tuple[np.ndarray, list]:
    
    # Input validation
    if len(hp_f) != len(hc_f) or len(hp_f) != len(freqs):
        raise ValueError("hp_f, hc_f, and freqs must have same length")
    
    # Ensure 1D arrays
    hp_f            = np.atleast_1d(hp_f)
    hc_f            = np.atleast_1d(hc_f)
    freqs           = np.atleast_1d(freqs)
    
    network         = gw.detection.Network(detector_ids=detector_ids, **({"config": config} if config else {}))
    
    # Combine polarizations into expected format
    polarizations   = np.column_stack([hp_f, hc_f])
    
    # Calculate time vector (dummy - will be replaced by geocent_time in projection)
    timevector      = np.ones_like(freqs) * sky_params.get("geocent_time", DEFAULT_GEOTIME)
    
    # Storage for projections
    all_projections = []
    detector_names  = []
    
    # Loop over detectors in network
    for detector in network.detectors:
        # Calculate projection for this detector
        detector.frequencyvector = freqs[:, None]
        proj = gw.detection.projection(
            parameters              =   sky_params,
            detector                =   detector,
            polarizations           =   polarizations,
            timevector              =   timevector,
            redefine_tf_vectors     =   False,
            long_wavelength_approx  =   lwa_approx
        )
        
        # Store results
        all_projections.append(proj)
        
        # Generate component names
        for comp_idx in range(proj.shape[1]):
            detector_names.append(f"{detector.name}_comp{comp_idx}")
    
    # Concatenate all projections
    projections = np.concatenate(all_projections, axis=1)
    return projections, detector_names


