import torch
import torch.nn.functional as F
from tqdm import tqdm


def evaluate(model, data_loader, metrics, device):
    if model.training:
        model.eval()

    summary = {metric: 0 for metric in metrics}

    for step, mb in tqdm(enumerate(data_loader), desc="steps", total=len(data_loader)):
        qa_mb, qb_mb, y_mb = map(lambda elm: (el.to(device) for el in elm) if isinstance(elm, tuple) else
        elm.to(device), mb)

        with torch.no_grad():
            y_hat_mb = model((qa_mb, qb_mb))

            for metric in metrics:
                summary[metric] += (
                    metrics[metric](y_hat_mb, y_mb).item() * y_mb.size()[0]
                )
    else:
        for metric in metrics:
            summary[metric] /= len(data_loader.dataset)

    return summary


def log_loss(inputs, targets):
    inputs = torch.log(inputs)
    loss = F.nll_loss(inputs, targets)
    return loss


def acc(yhat, y):
    with torch.no_grad():
        yhat = yhat.max(dim=1)[1]
        acc = (yhat == y).float().mean()
    return acc
