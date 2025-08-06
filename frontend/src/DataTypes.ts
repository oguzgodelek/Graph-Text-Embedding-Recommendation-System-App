export type Status = "loading" | "entrypoint" | "readyForInput" | "readyForOutput" | "initializationError" |
                     "processing" | "inputTypeError" | "inputError" | "search";

export interface Item {
   id: string,
   name: string,
   description: string
};

export interface ItemResponse {
    itemCount: number,
    itemList: Item[],
    message: string
}

export interface CollectionResponse {
    count: number,
    collectionList: string[],
    message: string
}
