"""Column-wise background-corrected laser stripe centroid extraction."""
import argparse
from pathlib import Path
import numpy as np

def extract(image, threshold=0.2):
    image=np.asarray(image,dtype=float)
    if image.ndim!=2 or min(image.shape)<2 or not np.isfinite(image).all():
        raise ValueError('Expected finite 2-D grayscale image')
    if not 0<threshold<1: raise ValueError('threshold must be between 0 and 1')
    signal=np.maximum(image-np.percentile(image,20,axis=0),0)
    peak=signal.max(axis=0)
    weights=np.where(signal>=threshold*peak,signal,0)
    # Normalize each nonzero column before summing weighted row coordinates.
    weights=np.divide(weights,peak[None,:],out=np.zeros_like(weights),where=peak[None,:]>0)
    total=weights.sum(axis=0)
    valid=(peak>max(float(np.max(peak))*.05,1e-9))&(total>0)
    center=np.full(image.shape[1],np.nan)
    center[valid]=(weights*np.arange(image.shape[0])[:,None]).sum(axis=0)[valid]/total[valid]
    return center,valid

def sample():
    rng=np.random.default_rng(42)
    rows,cols=np.mgrid[:180,:320]
    truth=75+20*np.sin(np.arange(320)/45)+np.arange(320)*.08
    image=5+180*np.exp(-.5*((rows-truth[None,:])/2)**2)+rng.normal(0,1,(180,320))
    return image,truth

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,help='2D grayscale .npy image; omitted uses synthetic data')
    parser.add_argument('--output',type=Path,default=Path('artifacts'))
    parser.add_argument('--threshold',type=float,default=.2)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    image,truth=(np.load(args.input,allow_pickle=False),None) if args.input else sample()
    center,valid=extract(image,args.threshold)
    np.savetxt(args.output/'stripe.csv',np.column_stack([np.arange(len(center)),center,valid]),delimiter=',',header='column,row,valid',comments='')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(12,5),layout='constrained')
    ax.imshow(image,cmap='inferno');ax.plot(center,color='cyan',lw=1,label='Extracted centroid')
    if truth is not None: ax.plot(truth,'w--',lw=.8,label='Synthetic ground truth')
    ax.set(title='Laser stripe extraction — synthetic demo' if truth is not None else 'Laser stripe extraction',xlabel='Column (px)',ylabel='Row (px)');ax.legend()
    fig.savefig(args.output/'result.png',dpi=150);plt.close(fig)
    if truth is not None:
        error=float(np.sqrt(np.mean((center[valid]-truth[valid])**2)))
        print(f'Synthetic RMSE: {error:.4f} px (not hardware accuracy)')
    print(f'Valid columns: {valid.sum()}/{len(valid)}')
if __name__=='__main__': main()
